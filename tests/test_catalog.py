"""Publication must never silently promote academic status or drift from sources."""
import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from catalog import validate
class CatalogTest(unittest.TestCase):
    def setUp(self):self.data=json.loads((Path(__file__).resolve().parents[1]/'data/catalog.json').read_text())
    def reject(self,change):
        data=copy.deepcopy(self.data);change(data['courses'])
        with self.assertRaises(AssertionError):validate(data)
    def test_false_completion(self):self.reject(lambda c:c[0].update(academic_status='lista'))
    def test_duplicate_slug(self):self.reject(lambda c:c.append(copy.deepcopy(c[0])))
    def test_wrong_domain_path(self):self.reject(lambda c:c[0].update(url='https://ustudyopen.github.io/'))
    def test_unreviewed_ready_page(self):self.reject(lambda c:c[0]['source']['metadata']['pages'][0].update(status='lista',reviewed=False))
    def test_unpinned_source(self):self.reject(lambda c:c[0]['source'].update(commit='main'))
    def test_valid_catalog(self):validate(self.data)
if __name__=='__main__':unittest.main()
