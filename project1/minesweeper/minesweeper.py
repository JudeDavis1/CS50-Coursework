import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if len(self.cells) == self.count:
            return set(self.cells)
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if self.count == 0:
            return set(self.cells)
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            return 1
        return 0

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells:
            self.cells.remove(cell)
            return 1
        return 0


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        counter = 0
        self.mines.add(cell)
        for sentence in self.knowledge:
            counter += sentence.mark_mine(cell)
        return counter

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        counter = 0
        self.safes.add(cell)
        for sentence in self.knowledge:
            counter += sentence.mark_safe(cell)
        return counter

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)

        i, j = cell
        others = set()

        for p in range(max(0, i - 1), min(i + 2, self.height)):
            for q in range(max(0, j - 1), min(j + 2, self.width)):
                if (p, q) != (i, j):
                    others.add((p, q))

        self.knowledge.append(Sentence(others, count))
        self.update_self_and_sentences()

        inferences = self.new_inferences()

        while inferences:
            for sentence in inferences:
                self.knowledge.append(sentence)

            self.update_self_and_sentences()

            inferences = self.new_inferences()


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        moves = self.safes.copy()
        moves -= self.moves_made

        if len(moves) == 0:
            return None

        return moves.pop()


    def _rand_cell(self):
        return (random.randrange(self.height), random.randrange(self.height))


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # 8 * 8 - 8 ---> 56
        if len(self.moves_made) == 56:
            return None

        random = self._rand_cell()
        unsafe_moves = self.moves_made | self.mines

        while random in unsafe_moves:
            random = self._rand_cell()

        return random

    def update_self_and_sentences(self):
        # repeat update if an update was made in the previous cycle
        i = 1
        while i:
            i = 0
            for sentence in self.knowledge:
                for cell in sentence.known_safes():
                    self.mark_safe(cell)
                    i += 1
                for cell in sentence.known_mines():
                    self.mark_mine(cell)
                    i += 1
            for cell in self.safes:
                i += self.mark_safe(cell)
            for cell in self.mines:
                i += self.mark_mine(cell)

    def new_inferences(self):
        removals = []
        inferences = []

        for sentence1 in self.knowledge:
            if sentence1.cells == set():
                removals.append(sentence1)
                continue

            for sentence2 in self.knowledge:
                if sentence2.cells == set():
                    removals.append(sentence2)
                    continue

                if sentence1 != sentence2:
                    if sentence2.cells.issubset(sentence1.cells):
                        diff_cells = sentence1.cells.difference(sentence2.cells)
                        diff_count = sentence1.count - sentence2.count

                        new_inference = Sentence(diff_cells, diff_count)

                        if new_inference not in self.knowledge:
                            inferences.append(new_inference)

        self.knowledge = [x for x in self.knowledge if x not in removals]

        return inferences
