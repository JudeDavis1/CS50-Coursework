import csv
import itertools
import sys
import math

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    
    probs = []
    children = set()

    # Helper function to return the likelihood of a gene being passed to a child
    def pass_probs(parent):
        if parent in one_gene:
            return .5
        
        elif parent in two_genes:
            return 1 - PROBS['mutation']
        
        return PROBS['mutation']

    # for kids with no parents (impossible!)
    for person in people:
        has_no_parents = people[person]['father'] is None and people[person]['mother'] is None

        if has_no_parents:
            if person in one_gene:
                prob_1gene = PROBS['gene'][1]
                prob_trait = PROBS['trait'][1][True] if person in have_trait else PROBS['trait'][1][False]
                
                # following the actual joint probability formulae
                probs.append(prob_1gene * prob_trait)
            
            elif person in two_genes:
                prob_2gene = PROBS['gene'][2]
                prob_trait = PROBS['trait'][2][True] if person in have_trait else PROBS['trait'][2][False]

                # again, follow the formula
                # if this were for production I would do it more efficiently but since we aren't, I'll just be quick...
                probs.append(prob_2gene * prob_trait)
            
            else:
                prob0 = PROBS['gene'][0]
                prob_trait = PROBS['trait'][0][True] if person in have_trait else PROBS['trait'][0][False]

                probs.append(prob0 * prob_trait)
        else:
            children.add(person)
        
    # this loop is for people WITH parents
    for child in children:
        # these return simple probabilities that the child has a gene from their parents
        from_m = pass_probs(people[child]['mother'])
        from_f = pass_probs(people[child]['father'])

        # inverse probabilities given by re-arranging the formula for probs.
        # total probs (1) - probability
        not_by_m = 1 - pass_probs(people[child]['mother'])
        not_by_f = 1 - pass_probs(people[child]['father'])
        
        if child in one_gene:
            prob_trait = PROBS['trait'][1][True] if child in have_trait else PROBS['trait'][1][False]
            # summation
            p = (from_m * not_by_f + from_f * not_by_m) * prob_trait
            probs.append(p)
        
        elif child in two_genes:
            prob_trait = PROBS['trait'][2][True] if child in have_trait else PROBS['trait'][2][False]
            p = (from_f * from_m) * prob_trait

            probs.append(p)

        else:
            prob_trait = PROBS['trait'][0][True] if child in have_trait else PROBS['trait'][0][False]
            p = (not_by_f * not_by_m) * prob_trait

            probs.append(p)
    
    return math.prod(probs)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # pretty straight-forward
    for prob in probabilities:
        if prob in one_gene:
            probabilities[prob]['gene'][1] += p
        
        elif prob in two_genes:
            probabilities[prob]['gene'][2] += p
        
        else:
            probabilities[prob]['gene'][0] += p
        
        if prob in have_trait:
            probabilities[prob]['trait'][True] += p
        
        else:
            probabilities[prob]['trait'][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for prob in probabilities:
        N = sum(list(probabilities[prob]['gene'].values()))

        for k, v in probabilities[prob]['gene'].items():
            # normalize 'gene' probability distribution
            probabilities[prob]['gene'][k] = v / N if N != 0 else v
        
        # normalize 'trait' probability distribution
        N = sum(list(probabilities[prob]['trait'].values()))

        for k, v in probabilities[prob]['trait'].items():
            probabilities[prob]['trait'][k] = v / N if N != 0 else v


if __name__ == "__main__":
    main()
