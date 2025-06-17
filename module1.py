import wikipediaapi

wiki= wikipediaapi.Wikipedia('en')
page= wiki.page("Python (programming language)")

if page.exists():
    print("Page Title:", page.title)
    print("Page Summary:", page.summary[:60])
    else:
        print("Page does not exist.")
