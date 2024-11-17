# from langchain_core.prompts import PromptTemplate
# import json

def get_prompt():
    return """
You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them.

Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). Parentheses have the highest priority, followed by Exponents, then Multiplication and Division, and lastly Addition and Subtraction.

For example:

Q. 5 + 10 / 2
Division first: (10 / 2) => 5, then Addition: 5 + 5 = 10.

Q. 2 + 3 + 5 * 4 - 8 / 2 
Multiplication and Division first: (5 * 4) => 20, (8 / 2) => 4, 
Then Addition and Subtraction from left to right: (2 + 3) => 5, (5 + 20) => 25, (25 - 4) => 21.

You can have three types of equations/expressions in this image, and only one case shall apply every time:

Following are the cases:

1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer as JSON:
{{
    "type": "simple_expression",
    "expression": "given expression",
    "result": "calculated answer"
}}
2. Set of equations or mathematical expressions with variables like :
Q.  x=3,
    y=2,
    2x+y=?

In this case solve them mathematically and return the solution as JSON format :
{{
    "type": "variable_expression",
    "expression": "given expression",
    "result": "calculated answer"
}}

4. Analyzing graphical math problems, such as cars colliding, trigonometric problems, problems on the Pythagorean theorem, adding runs from a cricket wagon wheel, etc.: In this case, analyze the drawing and accompanying information, and return the solution as JSON:
{{
    "type": "graphical_math_problem",
    "problem": "description of the problem",
    "result": "calculated answer"
}}
5. Detecting abstract concepts represented in a drawing, such as love, hate, jealousy, patriotism, or a historic reference to war, invention, discovery, quote, etc.: In this case, return the abstract concept as JSON:
{{
    "type": "abstract_concept",
    "description": "explanation of the drawing",
    "concept": "detected abstract concept"
}}

Analyze the equation or expression in this image and return the answer according to the given rules.


Return the answer strictly in the specified JSON format. Ensure proper key-value quoting for easier parsing with JSON parsers. Avoid any markdown or text formatting.
"""

