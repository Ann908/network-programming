from flask import Flask
from flask import request
app = Flask(__name__)
@app.route("/", methods=['GET', 'POST'])
def data_f():
    if request.method == 'GET':
        return "Hello World!"
    elif request.method == 'POST':
        data = request.get_data(as_text=True)
        try:
            with open("d.txt", "a", encoding='utf-8') as file:
                writing_file = file.write(data + "\n")
                print(writing_file)
                return data
        except OSError: #Problems with file system, for example not enough space
            return "File writing error", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

