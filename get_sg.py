#!/usr/bin/env python3

import json
import sys
import argparse
import os

escape_filename = lambda name: name.replace(' ', '_')

class Question:
    """Class to represent an individual question from the AP Classroom data"""

    def __init__(self, question_data):
        self.data = question_data
                
    def get_statement(self):
        """Get the question statement"""
        return self.data['stimulus']
    
    def get_options(self):
        """Get the list of options"""
        return {option['value']: option['label'] for option in self.data['options']}
    
    def get_answer_choice(self):
        """Get the answer choice letter (A, B, C, D, E)"""
        # table =  if self.is_zero_indexed else ['', 'A', 'B', 'C', 'D', 'E']
        all_options = self.get_options()
        answer_key = self.data['validation']['valid_response']['value'][0]
        answer_full_text = all_options[answer_key]
        result = ['A', 'B', 'C', 'D', 'E'][list(all_options.values()).index(answer_full_text)]
        return result
    
    def get_score(self):
        """Get the score value for the question"""
        return self.data['validation']['valid_response']['score']
    
    def stringify_options(self):
        """Format options as HTML with proper styling classes"""
        result_html = "<div class='options'>"
        for i, option_tuple in enumerate(self.get_options().items()):
            option_class = "option"
            id, option = option_tuple
            if ['A', 'B', 'C', 'D', 'E'][i] == self.get_answer_choice():
                option_class += " correct-answer"
            result_html += f"<div class='{option_class}'><div class='option-label'>{['A', 'B', 'C', 'D', 'E'][i]}.</div> {option}</div>"
        result_html += "</div>"
        return result_html

class Feature:
    """Class to represent 'feature' in JSON data, eg. reading passages and longer problem statements"""
    def __init__(self, feature_data):
        self.data = feature_data
        self.id = feature_data['feature_id']
        self.type = feature_data['type']
        self.content = feature_data['content']
    
    def stringify(self):
        """Format options as HTML with proper styling classes"""
        if self.id == -1:
            return ""

        feature_class = 'feature'
        if 'passage' in self.type:
            feature_class = 'passage'
        
        result_html = f"<div class='{feature_class}'>" + self.content + "</div>"
        return result_html


class Tag:
    """Class to represent a tag from the AP Classroom data"""
    
    def __init__(self, tag_data):
        self.data = tag_data
    
    def stringify(self):
        """Format tag as HTML list with proper styling"""
        result_html = "<div class='tag-list'><list>\n"
        for item in self.data:
            result_html += f"<li>{item}</li>"
        result_html += "<li>Important: Question fetched by AP Classroom Parser, do not share!</li>"
        result_html += "</list></div>\n"
        return result_html


class APClassroomParser:
    """Main class for parsing AP Classroom data and generating scoring guides"""
    

    def __init__(self, data, type, name=None):
        self.data = data
        self.all_questions_data = [item['questions'][0] for item in data['data']['apiActivity']['items']]
        self.all_features_data = [item['features'][0] if len(item['features']) > 0 else {"feature_id": -1, "type": "Unavailable", "content": "Unavailable"} for item in data['data']['apiActivity']['items']]
        
        if type == 'quiz':
            self.all_tags_data = [tag_item for tag_item in data['data']['apiActivity']['tags'].values()]
        elif type == 'result':
            self.all_tags_data = [['Unavailable'] for question in self.all_questions_data]
        self.activity_name = data['data']['apiActivity']['questionsApiActivity']['name'] if name == None else name
    
    def get_tag_by_index(self, index):
        """Get tag data by index (1-based)"""
        return Tag(self.all_tags_data[index - 1])
    
    def get_feature_by_index(self, index):
        """Get the feature data by index (1-based)"""
        return Feature(self.all_features_data[index - 1])
    
    def generate_scoring_guide(self):
        """Generate the HTML scoring guide with AP-style CSS"""

        template_path = os.path.join("front_end", "scoring_guide_template.html")
        stylesheet_path = os.path.join("front_end", "scoring_guide.css")

        with open(template_path, "r") as template_file:
            template_html = template_file.read()

        with open(stylesheet_path, "r") as stylesheet_file:
            stylesheet_css = stylesheet_file.read()

        questions_html = ""
        all_answers = []
        for i, question_data in enumerate(self.all_questions_data, 1):
            question = Question(question_data)
            tag = self.get_tag_by_index(i)
            feature = self.get_feature_by_index(i)

            questions_html += f'''
            <div class="question" id="question-{i}">
                <div class="question-header">
                    <div><span onclick="javascript:jump_from({i})">Question {i}</span> (<a href="#question-{i-1}">Previous</a> <a href="#question-{i+1}">Next</a>)</div> <span class="points">{question.get_score()} {"pt" if question.get_score() == 1 else "pts"}</span>
                </div>
                <div class="question-content">
                    {('<div class="feature">' + feature.stringify() + '</div>') if len(feature.stringify()) > 0 else ''}
                    <div class="statement">{question.get_statement()}</div>
                    <h3>Choices</h3>
                    {question.stringify_options()}
                    <h3>Tags</h3>
                    {tag.stringify()}
                </div>
            </div>
            '''
            all_answers.append(question.get_answer_choice())

        sg_html = template_html.replace("{{ activity_name }}", self.activity_name)
        sg_html = sg_html.replace("{{ questions_html }}", questions_html)
        sg_html = sg_html.replace("{{ stylesheet_css }}", stylesheet_css)

        return sg_html, all_answers
    
    def write_scoring_guide(self):
        """Write the scoring guide to a file and print information"""
        sg_html, all_answers = self.generate_scoring_guide()
        
        filename = f"scoring_guide_{self.activity_name}.html"
        filename = escape_filename(filename)
        
        with open(filename, "w") as fout:
            fout.write(sg_html)
        
        print(f'[*] Name: {self.activity_name}')
        print(f'[+] ans = {all_answers}')
        print(f'[+] Written: {filename}')
        
        return filename


class SATQuestion:
    """Class to represent an individual SAT question"""
    
    def __init__(self, question_data, section_name):
        self.data = question_data
        self.section = section_name

    def get_number(self):
        return int(self.data.get('displayNumber'))

    def get_passage(self):
        return self.data.get('passage', {}).get('body', '').replace('<span class=\"sr-only\">blank</span>', '')

    def get_statement(self):
        """Get the question statement"""
        return self.data.get('prompt', '')
    
    def get_options(self):
        """Get the options dict {'A': "xxx"}"""
        items = self.data.get('answer', {}).get('choices', {})
        # print(items)
        return {key: items.get(key).get('body') for key in items.keys()}
    
    def get_answer_choice(self):
        return self.data.get('answer', {}).get('correctChoice')
    
    def is_correct(self):
        return self.data.get('answer', {}).get('correct') == True
    
    def get_wrong_answer(self):
        return self.data.get('answer', {}).get('response') if not self.is_correct() else None

    def stringify_options(self):
        """Format options as HTML with proper styling classes"""
        result_html = "<div class='options'>"
        options = self.get_options()
        for letter in options:
            option_class = "option"
            if letter == self.get_answer_choice():
                option_class += " correct-answer"
            if letter == self.get_wrong_answer():
                option_class += " wrong-answer"
            result_html += f"<div class='{option_class}'><div class='option-label'>{letter}.</div> {options[letter]}</div>"
        result_html += "</div>"
        return result_html

    def get_rationale(self):
        """Get explanation for the correct answer"""
        return self.data.get('answer', {}).get('rationale', '')

    def get_score(self):
        """Get question score (always 1 for SAT)"""
        return 1
    
    def stringify(self):
        """Format the question as HTML with proper styling"""
        return f'''
        <div class="question-content">
            {(f'<div class="feature">{self.get_passage()}</div>') if len(self.get_passage()) > 0 else ''}
            <div class="statement">{self.get_statement()}</div>
            <h3>Choices</h3>
            {self.stringify_options()}
            {(f'<h3>Wrong Answer: {self.get_wrong_answer()}</h3>') if self.get_wrong_answer() != None else ''}
            <div class="rationale">
                <h3>Explanation</h3>
                {self.get_rationale()}
            </div>
        </div>
        '''

class SATSection:
    """Class to represent a section (Reading/Math) in SAT data"""
    
    def __init__(self, section_data, subset='full'):
        self.name = section_data.get('id', 'Unknown').lower()
        self.items = section_data.get('items', [])
        self.subset = subset

    def stringify(self):
        """Format section as HTML"""
        questions = [SATQuestion(item, self.name) for item in self.items]
        if self.subset == 'wrong':
            for question in questions:
                if question.is_correct() == True:
                    questions.remove(question)
        questions.sort(key=lambda question: question.get_number())
        html = f'<h2>Section: {self.name.upper()}</h2>'
        for i, question in enumerate(questions, start=1):
            html += f'''
            <div class="question" id="{self.name}-question-{i}">
                <div class="question-header">
                    <div><span onclick="javascript:jump_from({i}, '{self.name}')">Question {i}</span> 
                    (<a href="#{self.name}-question-{i-1}">Previous</a> <a href="#{self.name}-question-{i+1}">Next</a>)</div>
                    <span class="points">1 pt</span>
                </div>
                
                {question.stringify()}
            </div>
            '''
        return html

class SATParser:
    """Parser for SAT JSON data"""
    
    def __init__(self, data, name="SAT Practice Test", subset='full'):
        self.sections = [SATSection(section, subset=subset) for section in data]
        self.activity_name = name
        self.subset = subset

    def generate_scoring_guide(self):
        """Generate HTML scoring guide using existing template"""
        template_path = os.path.join("front_end", "scoring_guide_template.html")
        stylesheet_path = os.path.join("front_end", "scoring_guide.css")

        with open(template_path, "r") as template_file:
            template_html = template_file.read()
        with open(stylesheet_path, "r") as stylesheet_file:
            stylesheet_css = stylesheet_file.read()

        questions_html = ""
        for section in self.sections:
            questions_html += section.stringify()

        sg_html = template_html.replace("{{ activity_name }}", self.activity_name)
        sg_html = sg_html.replace("{{ questions_html }}", questions_html)
        sg_html = sg_html.replace("{{ stylesheet_css }}", stylesheet_css)

        return sg_html, []  # Empty list since SAT doesn't use answer choices A-E
    
    def write_scoring_guide(self):
        """Write scoring guide to file"""
        sg_html, _ = self.generate_scoring_guide()
        filename = f"scoring_guide_{escape_filename(self.activity_name)}.html"
        
        with open(filename, "w") as fout:
            fout.write(sg_html)
        
        print(f'[*] Name: {self.activity_name}')
        print(f'[+] Written: {filename}')
        return filename

# Update main() function to handle SAT type
def main():
    """Main function to parse input and generate scoring guide"""

    # Initialize parser
    arg_parser = argparse.ArgumentParser(
        prog='get_sg.py',
        description='Generate scoring guides with high quality on AP Classroom and SAT students\' client-side data package.',
    )
    arg_parser.add_argument('filename', help='What\'s the name (with full directory) of your JSON data?')
    arg_parser.add_argument('--type', choices=['quiz', 'result', 'sat'], 
                          default='result', 
                          help='Data type: quiz/result page or SAT')
    arg_parser.add_argument('--title', help='Customize title for generated scoring guide')
    arg_parser.add_argument('--subset', help='Choose a subset of the questions, eg. wrong (SAT only)', choices=['full', 'wrong'], default='full')
    args = arg_parser.parse_args()
    
    with open(args.filename, 'r') as fin:
        data = json.load(fin)

    if args.type == 'sat':
        parser = SATParser(data, name=args.title, subset=args.subset)
    else:
        parser = APClassroomParser(data, type=args.type, name=args.title)
    
    parser.write_scoring_guide()


if __name__ == '__main__':
    main()