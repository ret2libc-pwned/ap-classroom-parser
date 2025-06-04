# AP Classroom Parser

Parse your CollegeBoard result page into a scoring guide html.

The tool can be used to parse

- `activity` data in AP Classroom
- `questions` data in SAT result page

## Features

- Offline caching most of the problem contents (text, images, equations, etc.) for review without login into CollegeBoard
- User friendly navigation features
  - Jumping to specific problems by clicking on problem numbers
  - Easily navigating back and forth using navigation buttons displayed on the top of each problem
- Filtering wrong answers and displaying answer explanations in parsed SAT results
  - Use `Ctrl + F` or `Command + F` and search for `Wrong Answer:` to find all problems you made mistakes on.

## Command Line Arguments

Access help documents through `./get_sg.py --help`,

```
usage: get_sg.py [-h] [--type {quiz,result,sat}] [--title TITLE] [--subset SUBSET] filename

Generate scoring guides with high quality on AP Classroom and SAT students' client-side data package.

positional arguments:
  filename              What's the name (with full directory) of your JSON data?

options:
  -h, --help            show this help message and exit
  --type {quiz,result,sat}
                        Data type: quiz/result page or SAT
  --title TITLE         Customize title for generated scoring guide
  --subset SUBSET       Choose a subset of the questions, eg. {1, 3, 5}
```

## IMPORTANT Disclaimer 
This tool is intended solely for offline caching of AP Classroom quiz content, to improve accessibility when College Board servers are slow or unresponsive. All generated materials (including but not limited to images, text, and answers) are copyrighted by their respective owners. Retrieved Scoring Guide files are for personal study use only—do not share, redistribute, or modify them. The developer is not responsible for any consequences resulting from the use of this tool.
