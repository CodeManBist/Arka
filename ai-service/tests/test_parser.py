from analysis.parser_factory import ParserFactory

code = """
function add(a,b){
    return a+b;
}
"""

parser = ParserFactory.get_parser("typescript")

tree = parser.parse(code)

print(tree.root_node)