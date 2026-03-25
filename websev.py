import socket
import threading
import mimetypes
import os

HOST = 'localhost'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server running at http://{HOST}:{PORT}")

# navigation bar CSS
css_navbar = """
<style>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    text-align: center;
}
.navbar {
    display: flex;
    justify-content: center;
    background-color: #333;
}
.navbar a {
    display: inline-block;
    color: #f2f2f2;
    text-align: center;
    padding: 14px 20px;
    text-decoration: none;
}
.navbar a:hover {
    background-color: #ddd;
    color: black;
}
.navbar a.active {
    background-color: #1531d1;
    color: white;
}
.content {
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}


.card {
    background-color: #f2f2f2;
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 20px;
    max-width: 800px;
    text-align: justify;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    margin-top: 20px;
}

.card h1 {
    text-align: center;
}

/* FADE IN */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.fade-in {
    animation: fadeIn 0.8s ease-out;
}


/* Media grid */
.media-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 20px;
    justify-items: center;
    align-items: center;
    width: 80%;
    margin-top: 20px;
}
.media-grid img {
    max-width: 100%;
    grid-columm: 1 / 2;
}
.media-grid video {
    max-width: 100%;
    grid-column: 2 / 3;
}
.media-grid audio {
    grid-column: 1 / 2; 
}
.media-page {
    background-color: #c6d1e2;
    min-height: 100vh;
    padding-top: 20px;
}

</style>

"""


def wrap_page(title, current_page, content, extra_class=""):
    navbar = f"""
    <div class="navbar">
        <a href="/index" class="{ 'active' if current_page=='home' else '' }">Home</a>
        <a href="/media" class="{ 'active' if current_page=='media' else '' }">Media</a>
        <a href="/about" class="{ 'active' if current_page=='about' else '' }">About</a>
    </div>
    """
    return f"""
    <html>
    <head><title>{title}</title>{css_navbar}</head>
    <body class="{extra_class}">
        {navbar}
        <div class="content">
            {content}
        </div>
    </body>
    </html>
    """
SP_description = """
Socket programming is a way of connecting two nodes on a network to communicate with each other. 
One socket(node) listens on a particular port at an IP, while the other socket reaches out to the other to form a connection. 
The server forms the listener socket while the client reaches out to the server. They are the real backbones behind web browsing. 
In simpler terms, there is a server and a client. Socket programming is started by importing the socket library and making a simple socket.
"""
About_descipt = """ 
Webserver involves creating a program that uses sockets to listen for and respond to client (browser) requests using protocols like HTTP or WebSocket. 
"""

# HTML pages
html_pages = {
    "/": wrap_page(
        "Home", "home",
        f'''
        <div class="card fade-in">
            <h1>Socket Programming</h1>
            <p>{SP_description.replace("\n", "<br>")} </p>
        </div>
        '''
    ),
    "/index": wrap_page(
        "Home", "home",
        f'''
        <div class="card fade-in">
            <h1>Socket Programming</h1>
            <p>{SP_description.replace("\n", "<br>")} </p>
        </div>
        '''
    ),
    "/about": wrap_page(
        "About", "about",
        f'''
        <div class="card fade-in">
            <h1>About</h1>
            <p>{About_descipt.replace("\n", "<br>")}</p>
        </div>
        '''
    ),
    "/media": wrap_page(
        "Media", "media",
        """
        <h1>Media Page</h1>
        <p>Enjoy multimedia below:</p>
        <div class="media-grid">
            <img src="/media/sample_image.jpg" alt="Sample Image">
            <video controls>
                <source src="/media/sample_video.mp4" type="video/mp4">
                Your browser does not support video.
            </video>
            <audio controls>
                <source src="/media/sample_audio.mp3" type="audio/mpeg">
                Your browser does not support audio.
            </audio>
        </div>
        """,
        extra_class="media-page"
    )
}

def handle_client(client_socket, client_address):
    print(f"Connection from {client_address}")
    request = client_socket.recv(1024).decode()
    if not request:
        client_socket.close()
        return

    # parse request
    request_line = request.splitlines()[0]
    path = request_line.split(" ")[1]

    # Serve static files
    if path.startswith("/media/"):
        file_path = "." + path
        if os.path.exists(file_path):
            ctype, _ = mimetypes.guess_type(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            header = f"HTTP/1.1 200 OK\r\nContent-Type: {ctype}\r\nContent-Length: {len(content)}\r\n\r\n"
            client_socket.sendall(header.encode() + content)
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFile not found"
            client_socket.sendall(response.encode())

    # Serve HTML pages
    elif path in html_pages:
        html = html_pages[path]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
        client_socket.sendall(response.encode())
    else:
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"
        client_socket.sendall(response.encode())

    client_socket.close()

# Main server loop
while True:
    client_socket, client_address = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True).start()
