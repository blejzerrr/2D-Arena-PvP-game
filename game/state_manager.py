class state():
    def __init__(self, game):
        self.game = game # reference to main game object for accessing shared data
        self.next_state = None # name of state that's below current state

    def update(self, delta_time, actions):
        pass
    def render(self, surface):
        pass 

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self) # add this state to the stack, making it the current active state

    def exit_state(self):
        self.game.state_stack.pop() # remove this state from the stack, returning to previous state if it exists