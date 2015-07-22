from flask import Flask,jsonify,g


app = Flask(__name__)
count = []


@app.before_request
def before_request():
	print count


@app.route('/')
def hello_world():
	count.append(1)
	g.count = count
	return 'Hello World!'

'''
g保存一个request的全局变量（译者：g保存的是当前请求的全局变量，不同的请求会有不同的全局变量，通过不同的thread id区别）
'''
@app.route('/get')
def get():
	return jsonify(count=g.count)


if __name__ == '__main__':
	app.run(debug=True)