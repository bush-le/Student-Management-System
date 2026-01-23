"""
Utility class for pagination support
"""

class PaginationHelper:
    @staticmethod
    def paginate(items, page=1, per_page=50):
        """
        Paginate a list of items
        
        Args:
            items: List of items to paginate
            page: Current page (1-indexed)
            per_page: Items per page
            
        Returns:
            dict with 'data', 'page', 'total_pages', 'total_items'
        """
        total = len(items)
        total_pages = (total + per_page - 1) // per_page
        
        # Validate page number
        page = max(1, min(page, total_pages if total_pages > 0 else 1))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'data': items[start:end],
            'page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }

    @staticmethod
    def paginate_sql(sql_base, total_query, page=1, per_page=50, params=()):
        """
        For SQL-based pagination (more efficient for large datasets)
        
        Args:
            sql_base: Base SELECT query (without LIMIT)
            total_query: Query to count total items
            page: Current page
            per_page: Items per page
            params: Query parameters
            
        Returns:
            dict with LIMIT clause added
        """
        offset = (page - 1) * per_page
        sql_paginated = f"{sql_base} LIMIT {per_page} OFFSET {offset}"
        
        return {
            'sql': sql_paginated,
            'offset': offset,
            'limit': per_page,
            'params': params
        }
