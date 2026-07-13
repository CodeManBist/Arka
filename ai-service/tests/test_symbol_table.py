from analysis.repository_parser import RepositoryParser

parser = RepositoryParser()

result = parser.parse_repository(
    r"C:\Users\sagar\OneDrive\Desktop\Arka\backend\repositories\RentSphere"
)

table = result["symbol_table"]

print(f"Total symbols: {len(table)}")

for symbol in table.symbols[:10]:
    print(symbol)