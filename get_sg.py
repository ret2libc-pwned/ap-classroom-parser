#!/usr/bin/env python3

import json
import sys
import argparse
import os


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
    

    def __init__(self, data, type):
        self.data = data
        self.all_questions_data = [item['questions'][0] for item in data['data']['apiActivity']['items']]
        self.all_features_data = [item['features'][0] if len(item['features']) > 0 else {"feature_id": -1, "type": "Unavailable", "content": "Unavailable"} for item in data['data']['apiActivity']['items']]
        
        if type == 'quiz':
            self.all_tags_data = [tag_item for tag_item in data['data']['apiActivity']['tags'].values()]
        elif type == 'result':
            self.all_tags_data = [['Unavailable'] for question in self.all_questions_data]
        self.activity_name = data['data']['apiActivity']['questionsApiActivity']['name']
    
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
                    <a href="javascript:jump_from({i})">Question {i}</a> <span class="points">{question.get_score()} {"pt" if question.get_score() == 1 else "pts"}</span>
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

        escape_filename = lambda name: name.replace(' ', '_')
        
        filename = f"scoring_guide_{self.activity_name}.html"
        filename = escape_filename(filename)
        
        with open(filename, "w") as fout:
            fout.write(sg_html)
        
        print(f'[*] Name: {self.activity_name}')
        print(f'[+] ans = {all_answers}')
        print(f'[+] Written: {filename}')
        
        return filename


def main():
    """Main function to parse input and generate scoring guide"""

    # Initialize parser
    arg_parser = argparse.ArgumentParser(
        prog='get_sg.py',
        description='Generate scoring guides with high quality on AP Classroom students\' client-side data package.',
    )
    arg_parser.add_argument('filename', help='What\'s the name (with full directory) of your JSON data?')
    arg_parser.add_argument('--type', choices=['quiz', 'result'], default='result', help='Where did you get your JSON data? \'quiz\' page or \'result\' page?')
    args = arg_parser.parse_args()
    with open(args.filename, 'r') as fin:
        data = json.load(fin)

    parser = APClassroomParser(data, type=args.type)
    parser.write_scoring_guide()


if __name__ == '__main__':
    main()