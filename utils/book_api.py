import requests
from datetime import datetime

def search_book_by_title(title):
    """
    Search for book information using Google Books API.
    Returns book metadata if found, None otherwise.
    """
    if not title or not title.strip():
        return None

    try:
        # Google Books API endpoint
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': f'intitle:{title}',
            'maxResults': 5  # Get multiple results to find one with publisher info
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'items' not in data or len(data['items']) == 0:
            return None

        # Try to find the best match with most complete information
        best_match = None
        best_score = 0

        for item in data['items']:
            book_info = item['volumeInfo']

            # Calculate completeness score
            score = 0
            if book_info.get('title'):
                score += 1
            if book_info.get('authors'):
                score += 2
            if book_info.get('publisher'):
                score += 2  # Give higher weight to publisher
            if book_info.get('publishedDate'):
                score += 1
            if book_info.get('description'):
                score += 1

            # Prefer exact title matches
            if book_info.get('title', '').lower() == title.lower():
                score += 5

            if score > best_score:
                best_score = score
                best_match = book_info

        if not best_match:
            return None

        book_info = best_match

        # Extract relevant fields
        result = {
            'title': book_info.get('title', ''),
            'authors': ', '.join(book_info.get('authors', [])),
            'publisher': book_info.get('publisher', ''),
            'published_date': book_info.get('publishedDate', ''),
            'description': book_info.get('description', ''),
            'page_count': book_info.get('pageCount', ''),
            'categories': ', '.join(book_info.get('categories', [])),
            'isbn': '',
            'preview_url': book_info.get('previewLink', '')
        }

        # Extract ISBN if available (prefer ISBN_13 over ISBN_10)
        if 'industryIdentifiers' in book_info:
            isbn_13 = None
            isbn_10 = None
            for identifier in book_info['industryIdentifiers']:
                if identifier['type'] == 'ISBN_13':
                    isbn_13 = identifier['identifier']
                elif identifier['type'] == 'ISBN_10':
                    isbn_10 = identifier['identifier']

            # Use ISBN_13 if available, otherwise ISBN_10
            result['isbn'] = isbn_13 if isbn_13 else (isbn_10 if isbn_10 else '')

        # Parse and format publish date
        if result['published_date']:
            try:
                # Try parsing different date formats
                for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                    try:
                        date_obj = datetime.strptime(result['published_date'], fmt)
                        result['published_date'] = date_obj.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
            except:
                pass

        return result

    except requests.exceptions.RequestException as e:
        print(f"Error fetching book data: {e}")
        return None
    except Exception as e:
        print(f"Error processing book data: {e}")
        return None
