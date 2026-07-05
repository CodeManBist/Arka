from analysis.scanner import RepositoryScanner

scanner = RepositoryScanner()

files = scanner.scan(
    r"C:\Users\sagar\OneDrive\Desktop\Arka\backend\repositories\RentSphere"
)

for file in files:
    print(file)