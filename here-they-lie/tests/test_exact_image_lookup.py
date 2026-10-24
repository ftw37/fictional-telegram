"""Differential page-index tests for exact-start image lookup.

The independent oracle selects by start address and size, without traversing pages.
"""
import random
import unittest

PAGE=1<<20
MAX=(1<<64)-1

def choose(ids,images,address,size,valid):
    candidates=[i for i in ids if images[i][0]==address and (images[i][2] or not valid)]
    if len(candidates)==1:return candidates[0]
    return next((i for i in candidates if images[i][1]==size),None)

def lookup(images,pages,address,size,valid,fast):
    if size==0:return None
    length=1 if fast and size<=MAX-address else size
    last=((address+length-1)&MAX)//PAGE
    seen=set();ids=[]
    for page in range(address//PAGE,last+1):
        for i in pages.get(page,[]):
            start,n,_=images[i]
            if i not in seen and start<address+length and address<start+n:
                seen.add(i);ids.append(i)
    return choose(ids,images,address,size,valid)

def index(images):
    pages={}
    for i,(start,size,_) in enumerate(images):
        for page in range(start//PAGE,(start+size-1)//PAGE+1):pages.setdefault(page,[]).append(i)
    return pages

class ExactStartLookup(unittest.TestCase):
    def test_aliases_and_nonmatching_overlaps(self):
        images=[(PAGE-8,32,True),(PAGE,64,True),(PAGE,128,False),(PAGE+8,64,True)]
        pages=index(images)
        for valid in (False,True):
            for n in (1,64,128,8*PAGE):
                self.assertEqual(lookup(images,pages,PAGE,n,valid,False),
                                 lookup(images,pages,PAGE,n,valid,True))
        self.assertEqual(lookup(images,pages,PAGE,128,False,True),2)
        self.assertEqual(lookup(images,pages,PAGE,128,True,True),1)

    def test_empty_and_overflow(self):
        for address,size in [(0,0),(PAGE,0),(MAX-8,32)]:
            self.assertEqual(lookup([],{},address,size,True,False),
                             lookup([],{},address,size,True,True))

    def test_random_layouts_against_independent_oracle(self):
        rng=random.Random(574)
        checks=0
        for _ in range(32):
            images=[]
            for i in range(384):
                start=(rng.randrange(128)*PAGE+rng.choice((0,4,4096,PAGE-4)))
                if i and rng.randrange(4)==0:start=rng.choice(images)[0]
                images.append((start,rng.choice((4,64,4096,PAGE,2*PAGE,8*PAGE)),bool(rng.randrange(2))))
            pages=index(images)
            for _ in range(256):
                address=rng.choice(images)[0] if rng.randrange(3) else rng.randrange(128)*PAGE+17
                size=rng.choice((1,64,4096,PAGE,2*PAGE,8*PAGE,64*PAGE))
                for valid in (False,True):
                    expected=choose(range(len(images)),images,address,size,valid)
                    self.assertEqual(lookup(images,pages,address,size,valid,False),expected)
                    self.assertEqual(lookup(images,pages,address,size,valid,True),expected)
                    checks+=1
        print(f'Passed {checks} randomized exact-address page-index checks')

if __name__=='__main__':unittest.main()
