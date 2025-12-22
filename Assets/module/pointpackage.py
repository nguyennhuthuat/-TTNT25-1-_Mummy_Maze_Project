import time

class PersonalPointPackage:
    def __init__(self, max_score: int = 0, hint_penalty: int = 0, bonus_score: int = 0):
        self._max_score = max_score
        self._hint_penalty = hint_penalty
        self._bonus_score = bonus_score

        self._elapsed_time = 0
        self._start_counting = time.time()
        
        self._total_score = 0
        self._base_score = 0

    @property
    def max_score(self):
        return self._max_score
    
    @max_score.setter
    def max_score(self, value):
        if value < 0: value = 0
        self._max_score = value

    @property
    def base_score(self):
        return self._base_score
    
    @base_score.setter
    def base_score(self, value):
        if value < 0: value = 0
        self._base_score = value

    @property
    def bonus_score(self):
        return self._bonus_score
    
    @bonus_score.setter
    def bonus_score(self, value):
        if value < 0: value = 0
        self._bonus_score = value

    @property 
    def hint_penalty(self):
        return self._hint_penalty
    
    @hint_penalty.setter
    def hint_penalty(self, value):
        if value < 0: value = 0
        self._hint_penalty = value

    @property
    def elapsed_time(self):
        return self._elapsed_time
    
    @elapsed_time.setter
    def elapsed_time(self, value):
        if value < 0: value = 0
        self._elapsed_time = value

    @property
    def bonus_score(self):
        return self._bonus_score
    
    @bonus_score.setter
    def bonus_score(self, value):
        if value < 0: value = 0
        self._bonus_score = value


    @property
    def total_score(self):
        return self._total_score
    @total_score.setter
    def total_score(self, value):
        if value < 0: value = 0
        self._total_score = value

    def end_counting(self):
        self._elapsed_time = time.time() - self._start_counting

        # Calculate total score
        self._base_score = max(self._max_score//2, round(self._max_score - 5 * self._elapsed_time - self._hint_penalty * 0.01 * self._max_score + self._bonus_score))
        self._total_score += self._base_score + self._bonus_score

        return None
    
    def reset(self):
        self._elapsed_time = 0
        self._hint_penalty = 0
        self._bonus_score = 0
        self._base_score = 0
        self._start_counting = time.time()
        return None
    

class GlobalPointPackage:
    def __init__(self,BaseLevelScore: int = 0,hint_penalty: int = 0, bonus_score: int = 0, c: classmethod = PersonalPointPackage):
        self.player = c(BaseLevelScore, hint_penalty, bonus_score)

