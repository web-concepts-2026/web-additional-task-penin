import socket
import json

server = socket.socket()
server.bind(("localhost", 8000))
server.listen()
print("Server started on http://localhost:8000")

while True:
    conn, addr = server.accept()
    request = conn.recv(65536).decode()

    if not request:
        conn.close()
        continue

    parts = request.split("\r\n\r\n")
    head = parts[0]
    body = parts[1]

    lines = head.split("\r\n")
    first_line = lines[0].split(" ")
    method = first_line[0]
    full_path = first_line[1]

    headers = {}

    for line in lines[1:]:
        name_value = line.split(": ")
        headers[name_value[0]] = name_value[1]

    content_length = int(headers.get("Content-Length", 0))

    while len(body.encode()) < content_length:
        body += conn.recv(65536).decode()

    query = {}

    if "?" in full_path:
        path = full_path.split("?")[0]
        query_string = full_path.split("?")[1]

        for pair in query_string.split("&"):

            key_value = pair.split("=")
            query[key_value[0]] = key_value[1]


    else:
        path = full_path

    print("Request:", method, path, query)

    status = "200 OK"
    content_type = "text/html"

    if method == "GET" and path == "/":
        file = open("static/index.html")
        answer = file.read()
        file.close()

    elif method == "GET" and path == "/page":
        page_id = query.get("id", "none")
        answer = "<h1>Page</h1><p>id = " + page_id + "</p>"

    elif method == "POST" and path == "/api/echo":
        data = json.loads(body)
        result = {"received": data, "headers": headers}
        answer = json.dumps(result)
        content_type = "application/json"

    else:
        status = "404"
        answer = "<h1>404</h1>"

    response = "HTTP/1.1 " + status + "\r\n"
    response += "Content-Type: " + content_type + "\r\n"
    response += "Content-Length: " + str(len(answer.encode())) + "\r\n"
    response += "\r\n"
    response += answer

    conn.send(response.encode())
    
    conn.close()
