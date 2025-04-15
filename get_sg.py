#!/usr/bin/env python3

import json
import sys
import argparse


class Question:
    """Class to represent an individual question from the AP Classroom data"""

    def __init__(self, question_data):
        self.data = question_data
        self.is_zero_indexed = self._check_if_is_zero_indexed()

    def _check_if_is_zero_indexed(self):
        """Check if the options are zero-indexed"""
        all_option_symbols = [int(option['value'][1]) for option in self.data['options']]
        return min(all_option_symbols) == 0 or not(max(all_option_symbols) == 5)
        
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
        feature_class = 'feature'
        if 'passage' in self.type:
            feature_class = 'passage'
        
        result_html += f"<div class='{feature_class}'>" + self.content + "</div>"
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
        result_html += "</list></div>\n"
        return result_html


class APClassroomParser:
    """Main class for parsing AP Classroom data and generating scoring guides"""
    

    def __init__(self, data, type):
        self.data = data
        self.all_questions_data = [item['questions'][0] for item in data['data']['apiActivity']['items']]
        # self.all_features_data = [item['features'][0] for item in data['data']['apiActivity']['items']]

        # self.first_question_where_feature_displayed = {Feature(feature).id: -1 for feature in self.all_features_data}
        
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
        # Start with proper HTML5 document structure
        sg_html = f'''<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Scoring Guide for {self.activity_name} (AP Classroom)</title>
            <style>
            /* AP Classroom Scoring Guide Stylesheet */
            :root {{
              --ap-blue: #0056a6;
              --ap-dark-blue: #003366;
              --ap-light-blue: #e9f0f8;
              --ap-accent: #ff5a00;
              --ap-text: #333333;
              --ap-light-gray: #f5f5f5;
              --ap-border: #dddddd;
            }}
            
            body {{
              font-family: "Helvetica Neue", Arial, sans-serif;
              line-height: 1.6;
              color: var(--ap-text);
              margin: 0;
              padding: 0;
              background-color: white;
            }}
            
            .container {{
              max-width: 900px;
              margin: 0 auto;
              padding: 20px;
            }}
            
            /* Header Styling */
            .header {{
              background-color: var(--ap-blue);
              color: white;
              padding: 15px 20px;
              margin-bottom: 30px;
              border-bottom: 5px solid var(--ap-accent);
            }}
            
            h1 {{
              font-size: 24px;
              margin: 0;
              padding: 10px 0;
              color: var(--ap-blue);
              border-bottom: 2px solid var(--ap-blue);
              margin-bottom: 20px;
            }}
            
            .header h1 {{
              color: white;
              border-bottom: none;
              margin-bottom: 0;
            }}
            
            .important-notice {{
              background-color: #fff3e0;
              border-left: 4px solid var(--ap-accent);
              padding: 15px;
              margin-bottom: 25px;
              font-size: 14px;
            }}
            
            /* Question Styling */
            .question {{
              margin-bottom: 40px;
              border: 1px solid var(--ap-border);
              border-radius: 4px;
              overflow: hidden;
            }}
            
            .question-header {{
              background-color: var(--ap-light-blue);
              padding: 12px 15px;
              font-weight: bold;
              border-bottom: 1px solid var(--ap-border);
              display: flex;
              justify-content: space-between;
            }}
            
            .question-content {{
              padding: 20px;
              background-color: white;
            }}

            .feature {{
                paddint: 20px;
                background-color: white;
            }}

            .passage {{
                paddin
            }}
            
            h2 {{
              font-size: 18px;
              color: var(--ap-dark-blue);
              margin-top: 30px;
              margin-bottom: 15px;
              display: flex;
              align-items: center;
            }}
            
            h2::before {{
              content: "";
              display: inline-block;
              width: 6px;
              height: 20px;
              background-color: var(--ap-accent);
              margin-right: 10px;
            }}
            
            h3 {{
              font-size: 16px;
              color: var(--ap-blue);
              margin-top: 20px;
              margin-bottom: 10px;
              font-weight: 600;
            }}
            
            /* Options Styling */
            .options {{
              margin-bottom: 20px;
            }}
            
            .option {{
              display: flex;
              margin-bottom: 12px;
              padding: 10px;
              border: 1px solid var(--ap-border);
              border-radius: 4px;
              background-color: var(--ap-light-gray);
            }}
            
            .option-label {{
              font-weight: bold;
              min-width: 30px;
              color: var(--ap-dark-blue);
            }}
            
            .answer {{
              font-weight: bold;
              color: var(--ap-accent);
              font-size: 18px;
              padding: 10px;
              background-color: var(--ap-light-blue);
              display: inline-block;
              border-radius: 4px;
              border: 1px solid var(--ap-blue);
            }}
            
            /* Tags Styling */
            list {{
              display: block;
              margin: 0;
              padding: 0 0 0 20px;
            }}
            
            li {{
              margin-bottom: 6px;
              position: relative;
              list-style-type: none;
            }}
            
            li::before {{
              content: "•";
              color: var(--ap-accent);
              font-weight: bold;
              display: inline-block;
              width: 1em;
              margin-left: -1em;
            }}
            
            hr {{
              border: 0;
              height: 1px;
              background-color: var(--ap-border);
              margin: 30px 0;
            }}
            
            /* Footer */
            .footer {{
              text-align: center;
              margin-top: 40px;
              padding: 20px;
              font-size: 12px;
              color: #999;
              border-top: 1px solid var(--ap-border);
            }}
            
            /* Correct answer highlighting */
            .correct-answer {{
              background-color: #e7f5e8;
              border-left: 4px solid #28a745;
            }}
            
            .statement {{
              margin-bottom: 20px;
              line-height: 1.6;
            }}
            </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
                <h1>Scoring Guide for {self.activity_name}</h1>
            </div>
            
            <div class="important-notice">
                <strong>Important:</strong> This document is parsed from students' client-side data package (from a bug), which <i>should not</i> be accessed by students themselves.
                <br><strong>DO NOT SHARE THIS DOCUMENT!</strong>
            </div>
        '''
        
        all_answers = []
        # all_features = {}

        # for i, feature_data in enumerate(self.data):
            # feature = Feature(self.data[])
        
        for i, question_data in enumerate(self.all_questions_data, 1):
            question = Question(question_data)
            tag = self.get_tag_by_index(i)
            
            sg_html += f'''
            <div class="question">
                <div class="question-header">
                    Question {i} <span class="points">{question.get_score()} pt(s)</span>
                </div>
                <div class="question-content">
                    
                    <div class="statement">{question.get_statement()}</div>
                    
                    <h3>Choices</h3>
                    {question.stringify_options()}
                    
                    <h3>Answer</h3>
                    <div class="answer">{question.get_answer_choice()}</div>
                    
                    <h3>Tags</h3>
                    {tag.stringify()}
                </div>
            </div>
            '''
            
            all_answers.append(question.get_answer_choice())
        
        # Add footer
        sg_html += '''
            <div class="footer">
                © College Board | AP Classroom Scoring Guide (from AP Classroom Parser)
            </div>
        </div>
        </body>
        </html>
        '''
        
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
    arg_parser.add_argument('--type', choices=['quiz', 'result'], default='quiz', help='Where did you get your JSON data? \'quiz\' page or \'result\' page?')
    args = arg_parser.parse_args()
    with open(args.filename, 'r') as fin:
        data = json.load(fin)

    parser = APClassroomParser(data, type=args.type)
    parser.write_scoring_guide()


if __name__ == '__main__':
    main()