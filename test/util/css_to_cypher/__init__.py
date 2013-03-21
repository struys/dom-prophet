import unittest

from util import css_to_cypher as cc


class TestVariableGenerator(unittest.TestCase):
    
    def test_simple(self):
        gen = cc.var_name_generator()
        self.assertEqual(gen.next(), 'a')
        self.assertEqual(gen.next(), 'b')
        self.assertEqual(gen.next(), 'c')
        
    def test_beyond_single_characters(self):
        gen = cc.var_name_generator()
        for i in range(0, 26):
            gen.next()
            
        self.assertEqual(gen.next(), 'aa')
        self.assertEqual(gen.next(), 'ab')
        self.assertEqual(gen.next(), 'ac')
        
        
        for i in range(0, 23):
            gen.next()
            
        self.assertEqual(gen.next(), 'ba')
        self.assertEqual(gen.next(), 'bb')
        self.assertEqual(gen.next(), 'bc')
            

class TestParser(unittest.TestCase):
    
    def test_simple(self):
        gen = var_name_generator()
        var = cc.Variable(gen)
        x = cc.Query(
            cc.Start(
                  var,
                  cc.Node('*')
            ),
            cc.MatchClause(
                [cc.MatchRule(
                    cc.Variable(gen),
                    cc.Variable(gen),
                    'CHILD',
                    dist="single"
                )]
            ),
            None,
            cc.ReturnClause(
                    var
            )
        )
        
        self.assertEqual(x.__str__(), 'start a=node(*) match (b)-[:CHILD]->(c) return a')
        
        
class TestParse(unittest.TestCase):
    
    def test_element_selector(self):
        query = cc.calculate_neo4j_query('div')
        self.assertEqual(query.__str__(), "start a=node(*) where a.tagName='div' return a")
        
    def test_class_selector(self): 
        query = cc.calculate_neo4j_query('div.foo')
        self.assertEqual(query.__str__(), "start a=node(*) where has(a.class) and any(class in a.class where class='foo') and a.tagName='div' return a")
        
    def test_id_selector(self):
        query = cc.calculate_neo4j_query('div#foo')
        self.assertEqual(query.__str__(), "start a=node(*) where has(a.id) and a.id='foo' and a.tagName='div' return a")
        
    def test_class_without_element(self):
        query = cc.calculate_neo4j_query('.foo')
        
        self.assertEqual(query.__str__(), "start a=node(*) where has(a.class) and any(class in a.class where class='foo') return a")

    def test_combined_selector(self):
        query = cc.calculate_neo4j_query('div span')
        
        self.assertEqual(query.__str__(), "start a=node(*) match (a)-[:PARENT*]->(b) where a.tagName='div' and b.tagName='span' return b")

#    def test_many_combined_selector(self):
#        query = cc.calculate_neo4j_query('div span a')
#        
#        self.assertEqual(query.__str__(), "start a=node(*) match (a)-[:PARENT*]->(b), (b)-[:PARENT*]->(c) where a.tagName='div' and b.tagName='span' and c.tagName='a' return b")



if __name__ == '__main__':
    unittest.main()