from langchain_core.prompts import PromptTemplate
import json

def get_prompt(dict_of_vars):
    prompt = PromptTemplate.from_template("""
You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them.

Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). Parentheses have the highest priority, followed by Exponents, then Multiplication and Division, and lastly Addition and Subtraction.

For example:

Q. 2 + 3 * 4 (3 * 4) => 12, 2 + 12 = 14.

Q. 2 + 3 + 5 * 4 - 8 / 2 5 * 4 => 20, 8 / 2 => 4, 2 + 3 => 5, 5 + 20 => 25, 25 - 4 => 21.

You can have five types of equations/expressions in this image, and only one case shall apply every time:

Following are the cases:

1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer as JSON:
{{
    "type": "simple_expression",
    "expression": "given expression",
    "result": "calculated answer"
}}
2. Set of equations like x^2 + 2x + 1 = 0, 3y + 4x = 0, 5x^2 + 6y + 7 = 12, etc.: In this case, solve for the given variables, and return them as JSON:
{{
    "type": "set_of_equations",
    "variables": [
        {{"variable": "x", "result": "calculated value"}},
        {{"variable": "y", "result": "calculated value"}}
    ]
}}
3. Assigning values to variables like x = 4, y = 5, z = 6, etc.: In this case, assign values to variables and return them as JSON:
{{
    "type": "variable_assignment",
    "assignments": [
        {{"variable": "x", "value": "assigned value"}},
        {{"variable": "y", "value": "assigned value"}}
    ]
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

Make sure to use extra backslashes for escape characters like \\f -> \\f, \\n -> \\n, etc.

Here is a JSON object containing user-assigned variables. If the given expression has any of these variables, use their actual values from this JSON object:

{dict_of_vars}

Note : at the place of calculated answer and calculated value only answer to the expression should be present 
for example(if x and y is 3 and 4 respectively then) :
{{
     "type": "simple_expression",
        "expression": "2x+y",
        "result": 10
}}

   
        
Return the answer strictly in the specified JSON format. Ensure proper key-value quoting for easier parsing with JSON parsers. Avoid any markdown or text formatting.
""")
    out=prompt.invoke({"dict_of_vars": dict_of_vars})
    return out.text

