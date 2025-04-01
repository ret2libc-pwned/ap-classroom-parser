import json

def get_question_statement(question):
	return question['stimulus']

def get_options(question):
	return [option['label'] for option in question['options']]

def stringify_options(options):
	index = 0
	result_html = ""
	for option in options:
		result_html += f"<h4>{['A', 'B', 'C', 'D', 'E'][index]}. </h4>{option}"
		index += 1
	return result_html

def get_answer_choice(question):
	table = ['A', 'B', 'C', 'D', 'E'] if start_from_zero else ['', 'A', 'B', 'C', 'D', 'E']
	int(question['validation']['valid_response']['value'][0][1])
	return table[int(question['validation']['valid_response']['value'][0][1])]

def get_score(question):
	return question['validation']['valid_response']['score']

def get_tag(index):
	# index starts from 1
	return all_tags[index - 1]

def stringify_tag(tag):
	result_html = "<list>\n"
	for item in tag:
		result_html += f"<li>{item}</li>"
	result_html += "</list>\n"
	return result_html

def is_start_from_zero():
	start_from_zero = False 
	global all_questions
	if int(all_questions[0]['options'][0]['value'][1]) == 0:
		start_from_zero = True
	return start_from_zero

if __name__ == '__main__':
	with open("db.json", "r") as fin:
		data = json.load(fin)

	all_questions = [item['questions'][0] for item in data['data']['apiActivity']['items']]
	all_tags = [tag_item for tag_item in data['data']['apiActivity']['tags'].values()]
	start_from_zero = is_start_from_zero()

	name = data['data']['apiActivity']['questionsApiActivity']['name']

	sg_html = f'''
	<title>Scoring Guide for {name} (AP Classroom Parser)</title>
	<h1>Scoring Guide for {name}</h1>
	<b>Important:</b> This document is parsed from students' client-side data package (from a bug), which <i>should not</i> meant to be got by students themselves. 
	<b>DO NOT SHARE THIS DOCUMENT!!</b>
	'''

	question_no = 1

	for question in all_questions:
		sg_html += f'''<h2>Question {question_no} [{get_score(question)} pt (s)]</h2>
		{get_question_statement(question)}
		<h3>Choices</h3>
		{stringify_options(get_options(question))}
		<h3>Answer</h3>
		{get_answer_choice(question)}
		<h3>Tags</h3>
		{stringify_tag(get_tag(question_no))}
		<hr>
		'''
		question_no += 1

	with open("scoring_guide.html", "w") as fout:
		fout.write(sg_html)

	import os
	os.system("open scoring_guide.html")