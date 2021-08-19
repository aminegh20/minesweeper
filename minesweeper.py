import itertools
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
    return self.cells if len(self.cells) == self.count else None

  def known_safes(self):
    """
    Returns the set of all cells in self.cells known to be safe.
    """
    return self.cells if self.count == 0 else None

  def mark_mine(self, cell):
    """
    Updates internal knowledge representation given the fact that
    a cell is known to be a mine.
    """
    newcells = set()
    for maybe in self.cells:
      if maybe != cell:
        newcells.add(maybe)
      else:
        self.count -= 1
    
    self.cells = newcells


  def mark_safe(self, cell):
    """
    Updates internal knowledge representation given the fact that
    a cell is known to be safe.
    """
    newcells = set()
    for maybe in self.cells:
      if maybe != cell:
        newcells.add(maybe)
    
    self.cells = newcells

    # There is no need to update the counter!


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
    self.mines.add(cell)
    for sentence in self.knowledge:
      sentence.mark_mine(cell)

  def mark_safe(self, cell):
    """
    Marks a cell as safe, and updates all knowledge
    to mark that cell as safe as well.
    """
    self.safes.add(cell)
    for sentence in self.knowledge:
      sentence.mark_safe(cell)

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

    # Mark cell as one the moves made
    self.moves_made.add(cell)

    # Update all knowledge bases
    self.mark_safe(cell)

    # Get neighboring cells that are not yet clicked
    newcells, count = self.get_neighbors(cell, count)

    # Add new sentence to the AI's knowledge base
    newsentence = Sentence(newcells, count)
    self.knowledge.append(newsentence)
    
    # Mark safe if known as safe
    if (count == 0):
      for newcell in newcells:
        self.mark_safe(newcell)
    
    # Mark mine if known as mine
    if (len(newcells) == count):
      for newcell in newcells:
        self.mark_mine(newcell)

    # Draw new inferences
    inferences = []
    for sentence in self.knowledge:

      if sentence == newsentence:
        continue

      if sentence.cells.issubset(newcells):
        setdiff = newcells - sentence.cells
        cntdiff = count - sentence.count
        
        # Mine
        if len(setdiff) == cntdiff:
          for setdiffcell in setdiff:
            self.mark_mine(setdiffcell)
        
        # Safe
        elif cntdiff == 0:
          for setdiffcell in setdiff:
            self.mark_safe(setdiffcell)
        
        # Inference
        else:
          inferences.append(Sentence(setdiff, cntdiff))
      
      if sentence.cells.issuperset(newcells):
        setdiff = sentence.cells - newcells
        cntdiff = sentence.count - count
        
        # Mine
        if len(setdiff) == cntdiff:
          for setdiffcell in setdiff:
            self.mark_mine(setdiffcell)
        
        # Safe
        elif cntdiff == 0:
          for setdiffcell in setdiff:
            self.mark_safe(setdiffcell)
        
        # Inference
        else:
          inferences.append(Sentence(setdiff, cntdiff))

    # Extend current knowledge
    self.knowledge.extend(inferences)
    
    # Remove duplicates
    unique = []
    for sentence in self.knowledge:
      if sentence not in unique:
        unique.append(sentence)

    self.knowledge = unique
    
    # Final cleanup
    final = []
    for sentence in self.knowledge:
      if sentence.known_mines():
        for newmine in sentence.known_mines():
          self.mark_mine(newmine)
          continue
        
      if sentence.known_safes():
        for newsafe in sentence.known_safes():
          self.mark_safe(newsafe)
          continue
      
      final.append(sentence)
    
    self.knowledge = final

  def make_safe_move(self):
    """
    Returns a safe cell to choose on the Minesweeper board.
    The move must be known to be safe, and not already a move
    that has been made.

    This function may use the knowledge in self.mines, self.safes
    and self.moves_made, but should not modify any of those values.
    """
    safe_cells = self.safes - self.moves_made
    return safe_cells.pop() if len(safe_cells) > 0 else None

  def make_random_move(self):
    """
    Returns a move to make on the Minesweeper board.
    Should choose randomly among cells that:
      1) have not already been chosen, and
      2) are not known to be mines
    """
    all_moves = set()
    for i in range(self.height):
      for j in range(self.width):
        if (i, j) not in self.mines and (i, j) not in self.moves_made:
          all_moves.add((i, j))
    
    return random.choice(tuple(all_moves)) if len(all_moves) > 0 else None

  def get_neighbors(self, cell, count):

    # Store coordinates
    x, y = cell

    # Store result
    neighbors = set()
    
    # Get uncliked neighbors within bounds
    for i in range(-1, 2):
      for j in range(-1, 2):
        if (i == 0 and j == 0):
          continue
        if 0 <= x + i and x + i < self.height and 0 <= y + j and y + j < self.width:
          if not (x + i, y + j) in self.safes and not (x + i, y + j) in self.mines:
            neighbors.add((x + i, y + j))
          if ((x + i), (y + j)) in self.mines:
            count -= 1

    return neighbors, count
