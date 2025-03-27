import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import datetime
import time

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #26A69A;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stat-card {
        background: linear-gradient(135deg, #42a5f5 0%, #2196f3 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.8;
    }
    .success-msg {
        color: #4CAF50;
        font-weight: bold;
    }
    .error-msg {
        color: #F44336;
        font-weight: bold;
    }
    .creator-card {
        background: linear-gradient(135deg, #5c6bc0 0%, #3f51b5 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .profile-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .profile-img {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 5px solid white;
        margin: 0 auto;
        display: block;
        background-color: #7986cb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 50px;
        color: white;
    }
    .skill-tag {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.2);
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px;
        font-size: 0.9rem;
    }
    .social-icon {
        font-size: 1.5rem;
        margin: 0 10px;
        color: white;
    }
    .exit-btn {
        background-color: #f44336;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        margin-top: 20px;
    }
    .feature-icon {
        font-size: 24px;
        margin-right: 10px;
        color: #3f51b5;
    }
    .tech-pill {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# File handling functions
def save_library(library):
    with open('library.json', 'w') as file:
        json.dump(library, file)

def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as file:
            return json.load(file)
    return []

# Initialize the library
if 'library' not in st.session_state:
    st.session_state.library = load_library()
    
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
    
if 'filter_read' not in st.session_state:
    st.session_state.filter_read = "All"
    
if 'selected_book' not in st.session_state:
    st.session_state.selected_book = None
    
if 'book_to_mark' not in st.session_state:
    st.session_state.book_to_mark = ""
    
if 'book_to_remove' not in st.session_state:
    st.session_state.book_to_remove = ""
    
if 'exit_app' not in st.session_state:
    st.session_state.exit_app = False

# Header
st.markdown("<h1 class='main-header'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("", ["Library Dashboard", "Add Book", "Search Books", "Statistics", "About Creator", "Exit"])
    
    if page != "Exit":
        st.markdown("---")
        st.markdown("### Filters")
        filter_option = st.selectbox("Filter by status:", ["All", "Read", "Unread"])
        if filter_option != st.session_state.filter_read:
            st.session_state.filter_read = filter_option
        
        if st.button("Save Library", use_container_width=True):
            save_library(st.session_state.library)
            st.success("Library saved successfully!")

# Helper functions
def get_filtered_library():
    if st.session_state.filter_read == "All":
        return st.session_state.library
    
    if st.session_state.filter_read == "Read":
        return [book for book in st.session_state.library if book['read_status']]
    
    if st.session_state.filter_read == "Unread":
        return [book for book in st.session_state.library if not book['read_status']]

def get_library_stats():
    library = st.session_state.library
    total_books = len(library)
    if total_books > 0:
        read_books = sum(1 for book in library if book['read_status'])
        percent_read = (read_books / total_books) * 100
    else:
        read_books = 0
        percent_read = 0
    
    # Get genres count
    genres = {}
    for book in library:
        genre = book['genre']
        if genre in genres:
            genres[genre] += 1
        else:
            genres[genre] = 1
    
    # Get publication years distribution
    years = {}
    for book in library:
        year = book['publication_year']
        if year in years:
            years[year] += 1
        else:
            years[year] = 1
            
    return {
        "total": total_books,
        "read": read_books,
        "percent_read": percent_read,
        "genres": genres,
        "years": years
    }

def mark_book_as_read():
    if st.session_state.book_to_mark:
        found = False
        for book in st.session_state.library:
            if book['title'].lower() == st.session_state.book_to_mark.lower():
                book['read_status'] = True
                found = True
                st.session_state.book_mark_success = f"'{st.session_state.book_to_mark}' marked as read!"
                break
        if not found:
            st.session_state.book_mark_error = f"Book '{st.session_state.book_to_mark}' not found in your library."
        st.session_state.book_to_mark = ""

def remove_book():
    if st.session_state.book_to_remove:
        initial_len = len(st.session_state.library)
        st.session_state.library = [book for book in st.session_state.library if book['title'].lower() != st.session_state.book_to_remove.lower()]
        if len(st.session_state.library) < initial_len:
            st.session_state.book_remove_success = f"Book '{st.session_state.book_to_remove}' removed successfully!"
        else:
            st.session_state.book_remove_error = f"Book '{st.session_state.book_to_remove}' not found in your library."
        st.session_state.book_to_remove = ""

# Library Dashboard Page
if page == "Library Dashboard":
    st.markdown("<h2 class='sub-header'>My Library</h2>", unsafe_allow_html=True)
    
    # Quick stats in columns
    stats = get_library_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-label'>Total Books</div>
            <div class='stat-number'>{stats["total"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card' style='background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);'>
            <div class='stat-label'>Books Read</div>
            <div class='stat-number'>{stats["read"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card' style='background: linear-gradient(135deg, #7e57c2 0%, #5e35b1 100%);'>
            <div class='stat-label'>Read Percentage</div>
            <div class='stat-number'>{stats["percent_read"]:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display books
    st.markdown("<h3>Your Books</h3>", unsafe_allow_html=True)
    
    filtered_library = get_filtered_library()
    
    if not filtered_library:
        st.info("Your library is empty. Add some books to get started!")
    else:
        # Convert to DataFrame for better display
        df = pd.DataFrame(filtered_library)
        
        # Rename the columns for better display
        df = df.rename(columns={
            'title': 'Title',
            'author': 'Author',
            'publication_year': 'Year',
            'genre': 'Genre',
            'read_status': 'Read Status'
        })
        
        # Format the Read Status column
        df['Read Status'] = df['Read Status'].apply(lambda x: '✅ Read' if x else '📖 Unread')
        
        # Display the table
        st.dataframe(
            df[['Title', 'Author', 'Year', 'Genre', 'Read Status']], 
            use_container_width=True,
            height=400
        )
        
        # Book actions
        st.markdown("<h3>Book Actions</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>Mark Book as Read</h4>", unsafe_allow_html=True)
            book_to_mark = st.text_input("Enter book title:", key="mark_book_input")
            if st.button("Mark as Read", key="mark_read_btn", use_container_width=True):
                st.session_state.book_to_mark = book_to_mark
                mark_book_as_read()
            
            # Show success or error message
            if 'book_mark_success' in st.session_state and st.session_state.book_mark_success:
                st.success(st.session_state.book_mark_success)
                # Clear message after 3 seconds
                time.sleep(2)
                st.session_state.book_mark_success = ""
                st.rerun()
                
            if 'book_mark_error' in st.session_state and st.session_state.book_mark_error:
                st.error(st.session_state.book_mark_error)
                # Clear message after 3 seconds
                time.sleep(2)
                st.session_state.book_mark_error = ""
                st.rerun()
                
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>Remove Book</h4>", unsafe_allow_html=True)
            book_to_remove = st.text_input("Enter title of book to remove:", key="remove_book_input")
            if st.button("Remove Book", key="remove_book_btn", use_container_width=True):
                st.session_state.book_to_remove = book_to_remove
                remove_book()
            
            # Show success or error message
            if 'book_remove_success' in st.session_state and st.session_state.book_remove_success:
                st.success(st.session_state.book_remove_success)
                # Clear message after 3 seconds
                time.sleep(2)
                st.session_state.book_remove_success = ""
                st.rerun()
                
            if 'book_remove_error' in st.session_state and st.session_state.book_remove_error:
                st.error(st.session_state.book_remove_error)
                # Clear message after 3 seconds
                time.sleep(2)
                st.session_state.book_remove_error = ""
                st.rerun()
                
            st.markdown("</div>", unsafe_allow_html=True)

# Add Book Page
elif page == "Add Book":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    
    with st.form("add_book_form"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        title = st.text_input("Title", key="add_title")
        author = st.text_input("Author", key="add_author")
        
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=2023, key="add_year")
        with col2:
            genre = st.selectbox(
                "Genre", 
                ["Fiction", "Non-fiction", "Mystery", "Science Fiction", "Fantasy", "Biography", 
                 "History", "Self-help", "Romance", "Thriller", "Other"],
                key="add_genre"
            )
        
        read_status = st.checkbox("I have read this book", key="add_read_status")
        
        submitted = st.form_submit_button("Add Book", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if submitted:
            if not title or not author:
                st.error("Title and author are required fields!")
            else:
                # Check if book already exists
                if any(book['title'].lower() == title.lower() and book['author'].lower() == author.lower() for book in st.session_state.library):
                    st.error(f"'{title}' by {author} is already in your library!")
                else:
                    new_book = {
                        'title': title,
                        'author': author,
                        'publication_year': year,
                        'genre': genre,
                        'read_status': read_status
                    }
                    st.session_state.library.append(new_book)
                    save_library(st.session_state.library)
                    st.success(f"'{title}' by {author} added to your library!")

# Search Books Page
elif page == "Search Books":
    st.markdown("<h2 class='sub-header'>Search for Books</h2>", unsafe_allow_html=True)
    
    with st.expander("Search Options", expanded=True):
        search_type = st.radio("Search by:", ["Title", "Author", "Genre"])
        search_query = st.text_input(f"Enter {search_type.lower()} to search:", key="search_query")
        
        if st.button("Search", use_container_width=True):
            if search_query:
                results = []
                search_query = search_query.lower()
                
                for book in st.session_state.library:
                    if search_type == "Title" and search_query in book['title'].lower():
                        results.append(book)
                    elif search_type == "Author" and search_query in book['author'].lower():
                        results.append(book)
                    elif search_type == "Genre" and search_query in book['genre'].lower():
                        results.append(book)
                        
                st.session_state.search_results = results
                
                if not results:
                    st.info(f"No books found matching '{search_query}' in {search_type.lower()}.")
    
    # Display search results
    if st.session_state.search_results:
        st.markdown(f"<h3>Search Results ({len(st.session_state.search_results)} books found)</h3>", unsafe_allow_html=True)
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.search_results)
        
        # Rename the columns for better display
        df = df.rename(columns={
            'title': 'Title',
            'author': 'Author',
            'publication_year': 'Year',
            'genre': 'Genre',
            'read_status': 'Read Status'
        })
        
        # Format the Read Status column
        df['Read Status'] = df['Read Status'].apply(lambda x: '✅ Read' if x else '📖 Unread')
        
        # Display the table
        st.dataframe(
            df[['Title', 'Author', 'Year', 'Genre', 'Read Status']], 
            use_container_width=True,
            height=300
        )

# Statistics Page
elif page == "Statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    
    stats = get_library_stats()
    
    if stats["total"] == 0:
        st.info("Add some books to see your library statistics!")
    else:
        # Display stats in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Reading Progress</h3>", unsafe_allow_html=True)
            
            # Create a simple gauge chart for reading progress
            fig = px.pie(
                values=[stats["read"], stats["total"] - stats["read"]],
                names=["Read", "Unread"],
                color_discrete_sequence=["#4CAF50", "#BDBDBD"],
                hole=0.7,
            )
            fig.update_layout(
                annotations=[dict(text=f"{stats['percent_read']:.1f}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            <ul>
                <li>Total Books: {stats["total"]}</li>
                <li>Books Read: {stats["read"]}</li>
                <li>Books Unread: {stats["total"] - stats["read"]}</li>
                <li>Read Percentage: {stats["percent_read"]:.1f}%</li>
            </ul>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Genre Distribution</h3>", unsafe_allow_html=True)
            
            if stats["genres"]:
                genres_df = pd.DataFrame({
                    'Genre': list(stats["genres"].keys()),
                    'Count': list(stats["genres"].values())
                })
                
                fig = px.bar(
                    genres_df, 
                    x='Genre', 
                    y='Count',
                    color='Count',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(xaxis_title="Genre", yaxis_title="Number of Books")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No genre data available.")
                
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Publication Year Timeline
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Publication Years</h3>", unsafe_allow_html=True)
        
        if stats["years"]:
            years_df = pd.DataFrame({
                'Year': list(stats["years"].keys()),
                'Count': list(stats["years"].values())
            }).sort_values('Year')
            
            fig = px.line(
                years_df, 
                x='Year', 
                y='Count',
                markers=True,
                line_shape='linear'
            )
            fig.update_layout(xaxis_title="Publication Year", yaxis_title="Number of Books")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No publication year data available.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Most recent additions
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Your Reading Habits</h3>", unsafe_allow_html=True)
        
        # Calculate some interesting stats
        authors = {}
        for book in st.session_state.library:
            author = book['author']
            if author in authors:
                authors[author] += 1
            else:
                authors[author] = 1
        
        favorite_author = max(authors.items(), key=lambda x: x[1])[0] if authors else "None"
        favorite_genre = max(stats["genres"].items(), key=lambda x: x[1])[0] if stats["genres"] else "None"
        
        st.markdown(f"""
        <ul>
            <li>Favorite Author: {favorite_author} ({authors.get(favorite_author, 0)} books)</li>
            <li>Favorite Genre: {favorite_genre} ({stats["genres"].get(favorite_genre, 0)} books)</li>
            <li>Average Publication Year: {sum([int(year) * count for year, count in stats["years"].items()]) / stats["total"] if stats["years"] else "N/A":.0f}</li>
        </ul>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# About Creator Page
elif page == "About Creator":
    st.markdown("<h2 class='sub-header'>About the Creator</h2>", unsafe_allow_html=True)
    
    # Profile section with improved styling
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="creator-card">
            <div class="profile-header">
                <div class="profile-img">RH</div>
                <h2>Riaz Hussain</h2>
                <p>Software Developer & Book Enthusiast</p>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <div class="skill-tag">Python</div>
                <div class="skill-tag">Streamlit</div>
                <div class="skill-tag">Web Dev</div>
                <div class="skill-tag">UI/UX</div>
                <div class="skill-tag">Data Analysis</div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <a href="#" class="social-icon">🌐</a>
                <a href="#" class="social-icon">📧</a>
                <a href="#" class="social-icon">👨‍💻</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>About Me</h3>
            <p>Hello! I'm Riaz Hussain, a passionate software developer and book enthusiast. I've always been fascinated by the intersection of technology and literature, which led me to create this Personal Library Manager.</p>
            
            <p>With years of experience in software development, I specialize in creating beautiful, functional applications that solve real-world problems. I believe in clean code, intuitive design, and putting users first.</p>
            
            <h3>My Journey</h3>
            <p>My love for books started at an early age, and as my collection grew, I realized I needed a better way to organize and track my reading habits. This inspired me to build this application, combining my professional skills with my personal passion.</p>
            
            <p>When I'm not coding or reading, you can find me exploring new technologies, contributing to open-source projects, or sharing my knowledge with the community through workshops and mentoring.</p>
            
            <h3>Connect With Me</h3>
            <p>I'm always interested in connecting with fellow developers and book lovers. Feel free to reach out if you have suggestions for improving this application or if you just want to discuss your favorite books!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Project Information with improved styling
    st.markdown("<h3 class='sub-header'>About This Project</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Personal Library Manager</h3>
        <p>This application was created to help book enthusiasts manage their personal book collections in a visually appealing and intuitive way. I wanted to build something that would not only be functional but also enjoyable to use.</p>
        
        <h3>Key Features</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0;">
            <div style="flex: 1; min-width: 300px;">
                <p><span class="feature-icon">📚</span> <strong>Complete Book Management</strong></p>
                <p>Add, update, and remove books from your collection with ease. Mark books as read or unread to track your reading progress.</p>
            </div>
            <div style="flex: 1; min-width: 300px;">
                <p><span class="feature-icon">📊</span> <strong>Insightful Statistics</strong></p>
                <p>Visualize your reading habits with beautiful charts and graphs. See your favorite genres, authors, and reading progress.</p>
            </div>
            <div style="flex: 1; min-width: 300px;">
                <p><span class="feature-icon">🔍</span> <strong>Powerful Search</strong></p>
                <p>Quickly find books by title, author, or genre. No more searching through physical shelves.</p>
            </div>
            <div style="flex: 1; min-width: 300px;">
                <p><span class="feature-icon">💾</span> <strong>Automatic Saving</strong></p>
                <p>Your library is automatically saved, so you never have to worry about losing your data.</p>
            </div>
        </div>
        
        <h3>Technologies Used</h3>
        <div style="text-align: center; margin: 20px 0;">
            <span class="tech-pill">Python</span>
            <span class="tech-pill">Streamlit</span>
            <span class="tech-pill">Pandas</span>
            <span class="tech-pill">Plotly</span>
            <span class="tech-pill">JSON</span>
        </div>
        
        <h3>Future Plans</h3>
        <p>I'm continuously working to improve this application. Future updates may include:</p>
        <ul>
            <li>Book recommendations based on your reading history</li>
            <li>Integration with online book databases</li>
            <li>Reading challenges and goals</li>
            <li>Mobile companion app</li>
        </ul>
        
        <p style="text-align: center; margin-top: 30px; font-style: italic;">Thank you for using my Personal Library Manager!</p>
    </div>
    """, unsafe_allow_html=True)

# Exit Page
elif page == "Exit":
    st.markdown("<h2 class='sub-header'>Exit Application</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("""
    <h3>Thank You for Using Personal Library Manager</h3>
    <p>Your library has been automatically saved. You can safely close this browser tab or window.</p>
    
    <p>Would you like to save your library one last time before exiting?</p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save and Exit", use_container_width=True):
            save_library(st.session_state.library)
            st.success("Library saved successfully!")
            st.markdown("""
            <div class="exit-btn">
                You can now close this window
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Exit Without Saving", use_container_width=True):
            st.markdown("""
            <div class="exit-btn">
                You can now close this window
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display some stats before exiting
    stats = get_library_stats()
    if stats["total"] > 0:
        st.markdown("<h3>Your Library Summary</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-label'>Total Books</div>
                <div class='stat-number'>{stats["total"]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='stat-card' style='background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);'>
                <div class='stat-label'>Books Read</div>
                <div class='stat-number'>{stats["read"]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='stat-card' style='background: linear-gradient(135deg, #7e57c2 0%, #5e35b1 100%);'>
                <div class='stat-label'>Read Percentage</div>
                <div class='stat-number'>{stats["percent_read"]:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>© 2025 Personal Library Manager | Created by Riaz Hussain</p>", 
    unsafe_allow_html=True
)