import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide"
)

# File path for storing the library data
LIBRARY_FILE = "library.json"

# Function to load the library from a file
def load_library():
    if os.path.exists(LIBRARY_FILE):
        try:
            with open(LIBRARY_FILE, 'r') as file:
                return json.load(file)
        except Exception as e:
            st.error(f"Error loading library: {e}")
            return []
    else:
        return []

# Function to save the library to a file
def save_library(library):
    try:
        with open(LIBRARY_FILE, 'w') as file:
            json.dump(library, file, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Initialize session state variables if they don't exist
if 'library' not in st.session_state:
    st.session_state.library = load_library()
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = -1
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'last_saved' not in st.session_state:
    st.session_state.last_saved = None

# Main title
st.title("📚 Personal Library Manager")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Library", "Add Book", "Search", "Statistics"])

# Function to display book details
def display_book_card(book, index=None, show_actions=True):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(book["title"])
        st.write(f"**Author:** {book['author']}")
        st.write(f"**Year:** {book['year']}")
        st.write(f"**Genre:** {book['genre']}")
        st.write(f"**Status:** {'Read' if book['read'] else 'Unread'}")
    
    if show_actions and index is not None:
        with col2:
            st.write("")  # Add some spacing
            if st.button("Edit", key=f"edit_{index}"):
                st.session_state.edit_index = index
                st.rerun()
            
            if st.button("Delete", key=f"delete_{index}"):
                st.session_state.library.pop(index)
                save_library(st.session_state.library)
                st.session_state.last_saved = datetime.now().strftime("%H:%M:%S")
                st.rerun()
    
    st.markdown("---")

# Library page
if page == "Library":
    st.header("My Library")
    
    # Display last saved time if available
    if st.session_state.last_saved:
        st.sidebar.success(f"Last saved at {st.session_state.last_saved}")
    
    # Check if we're in edit mode
    if st.session_state.edit_index >= 0 and st.session_state.edit_index < len(st.session_state.library):
        st.subheader("Edit Book")
        book = st.session_state.library[st.session_state.edit_index]
        
        # Create a form for editing
        with st.form(key="edit_book_form"):
            title = st.text_input("Title", value=book["title"])
            author = st.text_input("Author", value=book["author"])
            year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=book["year"])
            genre = st.text_input("Genre", value=book["genre"])
            read = st.checkbox("Have you read this book?", value=book["read"])
            
            submit_button = st.form_submit_button(label="Update Book")
            cancel_button = st.form_submit_button(label="Cancel")
            
            if submit_button:
                # Update the book
                st.session_state.library[st.session_state.edit_index] = {
                    "title": title,
                    "author": author,
                    "year": int(year),
                    "genre": genre,
                    "read": read
                }
                save_library(st.session_state.library)
                st.session_state.last_saved = datetime.now().strftime("%H:%M:%S")
                st.session_state.edit_index = -1
                st.rerun()
            
            if cancel_button:
                st.session_state.edit_index = -1
                st.rerun()
    
    # Display all books
    if not st.session_state.library:
        st.info("Your library is empty. Go to the 'Add Book' page to add some books!")
    else:
        # Add sorting options
        sort_col, filter_col = st.columns(2)
        with sort_col:
            sort_by = st.selectbox("Sort by", ["Title", "Author", "Year", "Genre"])
        with filter_col:
            show_only = st.selectbox("Show only", ["All Books", "Read Books", "Unread Books"])
        
        # Apply filters
        filtered_library = st.session_state.library.copy()
        if show_only == "Read Books":
            filtered_library = [book for book in filtered_library if book["read"]]
        elif show_only == "Unread Books":
            filtered_library = [book for book in filtered_library if not book["read"]]
        
        # Apply sorting
        sort_key = sort_by.lower()
        if sort_key == "year":  # Special case for year to sort numerically
            filtered_library = sorted(filtered_library, key=lambda x: x[sort_key], reverse=True)
        else:
            filtered_library = sorted(filtered_library, key=lambda x: x[sort_key].lower())
        
        # Display the books
        for i, book in enumerate(filtered_library):
            # Find the original index in the library
            original_index = st.session_state.library.index(book)
            display_book_card(book, original_index)

# Add Book page
elif page == "Add Book":
    st.header("Add a New Book")
    
    with st.form(key="add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=2023)
        genre = st.text_input("Genre")
        read = st.checkbox("Have you read this book?")
        
        submit_button = st.form_submit_button(label="Add Book")
        
        if submit_button:
            if title and author:  # Basic validation
                # Check if book already exists (case-insensitive)
                book_exists = any(
                    book["title"].lower() == title.lower() and 
                    book["author"].lower() == author.lower() 
                    for book in st.session_state.library
                )
                
                if book_exists:
                    st.error(f"'{title}' by {author} already exists in your library!")
                else:
                    new_book = {
                        "title": title,
                        "author": author,
                        "year": int(year),
                        "genre": genre,
                        "read": read
                    }
                    
                    st.session_state.library.append(new_book)
                    save_library(st.session_state.library)
                    st.session_state.last_saved = datetime.now().strftime("%H:%M:%S")
                    st.success(f"'{title}' by {author} added to your library!")
            else:
                st.error("Title and author are required!")

# Search page
elif page == "Search":
    st.header("Search Your Library")
    
    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        search_type = st.selectbox("Search by", ["Title", "Author", "Genre", "Year"])
    
    with search_col2:
        if search_type == "Year":
            search_term = st.number_input("Enter year", min_value=1000, max_value=datetime.now().year, value=2023)
        else:
            search_term = st.text_input(f"Enter {search_type.lower()}")
    
    if st.button("Search") or search_term:
        if search_term:
            # Perform search
            if search_type == "Title":
                st.session_state.search_results = [
                    (i, book) for i, book in enumerate(st.session_state.library) 
                    if search_term.lower() in book["title"].lower()
                ]
            elif search_type == "Author":
                st.session_state.search_results = [
                    (i, book) for i, book in enumerate(st.session_state.library) 
                    if search_term.lower() in book["author"].lower()
                ]
            elif search_type == "Genre":
                st.session_state.search_results = [
                    (i, book) for i, book in enumerate(st.session_state.library) 
                    if search_term.lower() in book["genre"].lower()
                ]
            elif search_type == "Year":
                st.session_state.search_results = [
                    (i, book) for i, book in enumerate(st.session_state.library) 
                    if book["year"] == search_term
                ]
            
            # Display results
            if st.session_state.search_results:
                st.subheader(f"Found {len(st.session_state.search_results)} results")
                for index, book in st.session_state.search_results:
                    display_book_card(book, index)
            else:
                st.info(f"No books found matching '{search_term}' in {search_type.lower()}")
        else:
            st.warning("Please enter a search term")

# Statistics page
elif page == "Statistics":
    st.header("Library Statistics")
    
    if not st.session_state.library:
        st.info("Your library is empty. Add some books to see statistics!")
    else:
        # Basic statistics
        total_books = len(st.session_state.library)
        read_books = sum(1 for book in st.session_state.library if book["read"])
        unread_books = total_books - read_books
        percentage_read = (read_books / total_books) * 100 if total_books > 0 else 0
        
        # Display basic statistics in a nice layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Books", total_books)
        
        with col2:
            st.metric("Books Read", read_books)
        
        with col3:
            st.metric("Books Unread", unread_books)
        
        # Progress bar for read percentage
        st.subheader("Reading Progress")
        st.progress(percentage_read / 100)
        st.write(f"{percentage_read:.1f}% of your library has been read")
        
        # Create a DataFrame for easier analysis
        df = pd.DataFrame(st.session_state.library)
        
        # Genre distribution
        st.subheader("Genre Distribution")
        genre_counts = df["genre"].value_counts()
        st.bar_chart(genre_counts)
        
        # Publication years
        st.subheader("Books by Publication Decade")
        df["decade"] = (df["year"] // 10) * 10
        decade_counts = df["decade"].value_counts().sort_index()
        st.bar_chart(decade_counts)
        
        # Author statistics
        st.subheader("Top Authors")
        author_counts = df["author"].value_counts().head(5)
        st.bar_chart(author_counts)
        
        # Read vs Unread by genre
        st.subheader("Read vs Unread by Genre")
        read_by_genre = df.groupby(["genre", "read"]).size().unstack().fillna(0)
        if not read_by_genre.empty and read_by_genre.shape[1] == 2:  # Ensure we have both True and False columns
            read_by_genre.columns = ["Unread", "Read"]
            st.bar_chart(read_by_genre)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Personal Library Manager v1.0")
if st.sidebar.button("Save Library"):
    if save_library(st.session_state.library):
        st.session_state.last_saved = datetime.now().strftime("%H:%M:%S")
        st.sidebar.success(f"Library saved at {st.session_state.last_saved}")
    else:
        st.sidebar.error("Failed to save library") 