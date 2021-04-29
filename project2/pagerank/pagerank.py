import os
import re
import sys
import math
import random

DAMPING = 0.85
SAMPLES = 10000


def main():
	if len(sys.argv) != 2:
		sys.exit("Usage: python pagerank.py corpus")
	
	corpus = crawl(sys.argv[1])
	ranks = sample_pagerank(corpus, DAMPING, SAMPLES)

	print(f"PageRank Results from Sampling (n = {SAMPLES})")

	for page in sorted(ranks):
		print(f"  {page}: {ranks[page]:.4f}")
    
	ranks = iterate_pagerank(corpus, DAMPING)
	print(f"PageRank Results from Iteration")
    
	for page in sorted(ranks):
		print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
	"""
	Parse a directory of HTML pages and check for links to other pages.
	Return a dictionary where each key is a page, and values are
	a list of all other pages in the corpus that are linked to by the page.
	"""

	pages = dict()

	# Extract all links from HTML files
	for filename in os.listdir(directory):
		if not filename.endswith(".html"):
			continue
		
		with open(os.path.join(directory, filename)) as f:
			contents = f.read()
			links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
			pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
	for filename in pages:
		pages[filename] = set(
			link for link in pages[filename]
				if link in pages
		)

	return pages


def transition_model(corpus, page, damping_factor):
	"""
	Return a probability distribution over which page to visit next,
	given a current page.

	With probability `damping_factor`, choose a link at random
	linked to by `page`. With probability `1 - damping_factor`, choose
	a link at random chosen from all pages in the corpus.
	"""

	all_pages = len(corpus)

	if corpus[page]:
		prob = [(1 - damping_factor) / all_pages] * all_pages
		prob_dict = dict(zip(corpus.keys(), prob))

		# link probabilities
		linked = damping_factor / len(corpus[page])
		for link in corpus[page]:
			prob_dict[link] += linked

		return prob_dict
	
	return dict(zip(corpus.keys(), [1 / len(corpus)] * all_pages))


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    keys = corpus.keys()
    pageranks = dict(zip(keys, [0] * len(corpus)))
    page = random.choice(list(keys))

    for i in range(n - 1):
    	pageranks[page] += 1
    	prob = transition_model(corpus, page, damping_factor)
    	page = random.choices(list(prob.keys()), prob.values())[0]

    return {page: n_samples / n for page, n_samples in pageranks.items()}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)

    # assign each page a rank
    pageranks = dict(zip(corpus.keys(), [1 / N] * N))
    dy_pageranks = dict(zip(corpus.keys(), [math.inf] * N))

    # keep updating the pageranks model until the d/dx() change is none

    while any(change > 0.001 for change in dy_pageranks.values()):
    	for page in pageranks.keys():
    		link_prob = 0

    		for page_link, links in corpus.items():
    			if not links:
    				links = corpus.keys()

    			if page in links:
    				link_prob += pageranks[page_link] / len(links)

    		new_rank = ((1 - damping_factor) / N) + (damping_factor * link_prob)


    		# keep track of change within the page models
    		dy_pageranks[page] = abs(new_rank - pageranks[page])
    		pageranks[page] = new_rank

    return pageranks


if __name__ == "__main__":
    main()
