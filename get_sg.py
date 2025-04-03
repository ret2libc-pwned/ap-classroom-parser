#!/usr/bin/env python3
# usage: cat data.json | python get_sg.py

import json
import sys


class Question:
    """Class to represent an individual question from the AP Classroom data"""
    def __init__(self, question_data, is_zero_indexed):
        self.data = question_data
        self.is_zero_indexed = is_zero_indexed
        
    def get_statement(self):
        """Get the question statement"""
        return self.data['stimulus']
    
    def get_options(self):
        """Get the list of options"""
        return [option['label'] for option in self.data['options']]
    
    def get_answer_choice(self):
        """Get the answer choice letter (A, B, C, D, E)"""
        table = ['A', 'B', 'C', 'D', 'E'] if self.is_zero_indexed else ['', 'A', 'B', 'C', 'D', 'E']
        answer_index = int(self.data['validation']['valid_response']['value'][0][1])
        return table[answer_index]
    
    def get_score(self):
        """Get the score value for the question"""
        return self.data['validation']['valid_response']['score']
    
    def stringify_options(self):
        """Format options as HTML"""
        result_html = ""
        for i, option in enumerate(self.get_options()):
            result_html += f"<h4>{['A', 'B', 'C', 'D', 'E'][i]}. </h4>{option}"
        return result_html


class Tag:
    """Class to represent a tag from the AP Classroom data"""
    
    def __init__(self, tag_data):
        self.data = tag_data
    
    def stringify(self):
        """Format tag as HTML list"""
        result_html = "<list>\n"
        for item in self.data:
            result_html += f"<li>{item}</li>"
        result_html += "</list>\n"
        return result_html


class APClassroomParser:
    """Main class for parsing AP Classroom data and generating scoring guides"""
    
    def __init__(self, data):
        self.data = data
        self.all_questions_data = [item['questions'][0] for item in data['data']['apiActivity']['items']]
        self.all_tags_data = [tag_item for tag_item in data['data']['apiActivity']['tags'].values()]
        self.activity_name = data['data']['apiActivity']['questionsApiActivity']['name']
        self.is_zero_indexed = self._check_if_zero_indexed()
        
    def _check_if_zero_indexed(self):
        """Check if the options are zero-indexed"""
        return int(self.all_questions_data[0]['options'][0]['value'][1]) == 0
    
    def get_tag_by_index(self, index):
        """Get tag data by index (1-based)"""
        return Tag(self.all_tags_data[index - 1])
    
    def generate_scoring_guide(self):
        """Generate the HTML scoring guide"""
        sg_html = f'''
        <title>Scoring Guide for {self.activity_name} (AP Classroom Parser)</title>
        <h1>Scoring Guide for {self.activity_name}</h1>
        <b>Important:</b> This document is parsed from students' client-side data package (from a bug), which <i>should not</i> meant to be got by students themselves. 
        <b>DO NOT SHARE THIS DOCUMENT!!</b>
        '''
        
        all_answers = []
        
        for i, question_data in enumerate(self.all_questions_data, 1):
            question = Question(question_data, self.is_zero_indexed)
            tag = self.get_tag_by_index(i)
            
            sg_html += f'''<h2>Question {i} [{question.get_score()} pt(s)]</h2>
            {question.get_statement()}
            <h3>Choices</h3>
            {question.stringify_options()}
            <h3>Answer</h3>
            {question.get_answer_choice()}
            <h3>Tags</h3>
            {tag.stringify()}
            <hr>
            '''
            
            all_answers.append(question.get_answer_choice())
        
        return sg_html, all_answers
    
    def write_scoring_guide(self):
        """Write the scoring guide to a file and print information"""
        sg_html, all_answers = self.generate_scoring_guide()
        
        filename = f"scoring_guide_{self.activity_name}.html"
        with open(filename, "w") as fout:
            fout.write(sg_html)
        
        print(f'[*] Name: {self.activity_name}')
        print(f'[+] Written: {filename}')
        
        return filename


def main():
    """Main function to parse input and generate scoring guide"""
    data = json.load(sys.stdin)
    parser = APClassroomParser(data)
    parser.write_scoring_guide()


if __name__ == '__main__':
    main()