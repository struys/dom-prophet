import cssselect
import cssselect.parser
import string
from itertools import chain

def calculate_neo4j_query(css_selector):
    gen = var_name_generator()
    var = Variable(gen)
    query = Query(gen, start=Start(var, Node('*')), where_clause=[], match_clause=[])
    parsed_css = cssselect.parse(css_selector)[0].parsed_tree
    
    _calculate_neo4j_query(parsed_css, query, last_var=var)
    
    return query

def _calculate_neo4j_query(parsed_css, query, last_var=None):
    if parsed_css is None:
        return
    
    if isinstance(parsed_css, cssselect.parser.CombinedSelector):
        element1 = parsed_css.selector
        
#        if isinstance(element1, cssselect.parser.CombinedSelector):
#            last_var = Variable(query.gen)
#        else:
#            next_var = Variable(query.gen)
        
        next_var = Variable(query.gen)
        _calculate_neo4j_query(element1, query, last_var=last_var)
        
        match = MatchRule(last_var, next_var, 'PARENT')
        query.match_clause.append(match)
        _calculate_neo4j_query(parsed_css.subselector, query, last_var=next_var)
    if isinstance(parsed_css, cssselect.parser.Hash):
        query.where_clause.append(HasId(last_var, parsed_css.id))
        _calculate_neo4j_query(parsed_css.selector, query, last_var=last_var)
    if isinstance(parsed_css, cssselect.parser.Class):
        query.where_clause.append(HasClass(last_var, parsed_css.class_name))
        _calculate_neo4j_query(parsed_css.selector, query, last_var=last_var)
    elif isinstance(parsed_css, cssselect.parser.Element):
        if parsed_css.element is not None:
            expr1 = "{0}.tagName='{1}'".format(last_var, parsed_css.element)
            query.where_clause.append(expr1)
        
        query.return_clause = ReturnClause(last_var)

def parse(css_selector):
    
    if isinstance(parsed_css, Element):
        var = Variable()
        return Query(
            Start(var),
            return_value=ReturnClause(var)
        )

def var_name_generator():
    def letter_gen():
        for i in string.lowercase:
            yield i
            
    for i in letter_gen():
        yield i
        
    for i in var_name_generator():
        for j in letter_gen():
            yield i + j

class Variable(object):
    
    def __init__(self, gen):
        self.gen = gen    
        self.var_name = self.gen.next()
        
    def __str__(self):
        return self.var_name
    
class HasClass(object):
    
    def __init__(self, var, class_name):
        self.var = var
        self.class_name = class_name
        
    def __str__(self):
        return str(Conjunct(
            HasExpression(str(self.var) + '.class'),
            "any(class in {var}.class where class='{class_name}')".format(var=self.var, class_name=self.class_name)
        ))
        
class HasId(object):
    
    def __init__(self, var, id):
        self.var = var
        self.id = id
        
    def __str__(self):
        return str(Conjunct(
            HasExpression(str(self.var) + '.id'),
            "{var}.id='{id}'".format(var=self.var, id=self.id)
        ))
    
class Node(object):
    
    def __init__(self, var):
        self.var = var
        
    def __str__(self):
        return 'node({var})'.format(var=self.var)    
    
class Start(object):
    
    def __init__(self, var, node):
        self.var = var
        self.node = node
        
    def __str__(self):
        return 'start {var}={node}'.format(var=self.var, node=self.node)

class MatchClause(object):
    
    def __init__(self, match_rules):
        self.match_rules = match_rules
        
    def __str__(self):
        return 'match ' + ','.join([rule.__str__() for rule in self.match_rules])

class MatchRule(object):
    
    def __init__(self, var1, var2, relation, dist='many'):
        self.var1 = var1
        self.var2 = var2
        self.relation = relation
        self.dist = dist
        
    def __str__(self):
        return '({var1})-[:{relation}{dist}]->({var2})'.format(
            var1=self.var1,
            relation=self.relation,
            dist='*' if self.dist == 'many' else '',
            var2=self.var2,
        )

class WhereClause(object):
    
    def __init__(self, expr):
        self.expr = expr
        
    def __str__(self):
        return 'where {0}'.format(self.expr)

class BinaryExpression(object):
        
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return '{0} {1} {2}'.format(self.expr1, self.operator, self.expr2)

class Conjunct(BinaryExpression):
    operator = 'and'

class HasExpression(object):
    
    def __init__(self, expr):
        self.expr = expr
        
    def __str__(self):
        return 'has({0})'.format(self.expr)

class ReturnClause(object):

    def __init__(self, var):
        self.var = var
        
    def __str__(self):
        return 'return {var}'.format(var=self.var)
    
class Query(object):
    
    def __init__(self, gen, start, match_clause=None, where_clause=None, return_clause=None):
        self.gen = gen
        self.start = start
        self.match_clause = match_clause
        self.where_clause = where_clause
        self.return_clause = return_clause
        
    def __str__(self):
        buf = '{start}'.format(start=self.start)
        if len(self.match_clause) > 0:
            buf += ' match {match_clause}'.format(match_clause=', '.join([str(m) for m in self.match_clause]))
        if len(self.where_clause) > 0:
            buf += ' where {where_clause}'.format(where_clause=' and '.join(str(w) for w in self.where_clause))
            
        buf += ' {return_clause}'.format(return_clause=self.return_clause)
            
        return buf