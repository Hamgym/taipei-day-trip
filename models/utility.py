def get_next_page(page, rows):
  if len(rows) < 12:
    return None
  return page + 1