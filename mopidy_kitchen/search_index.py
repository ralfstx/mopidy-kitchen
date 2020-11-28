import logging
from typing import Set


logger = logging.getLogger(__name__)


class SearchIndex:
    def __init__(self):
        self._index = {}
        self._sorted = []
        self._dirty = False

    def add(self, string: str, result: str):
        for word in string.lower().split():
            if len(word) > 1:
                if word not in self._index:
                    self._index[word] = set()
                self._index[word].add(result)
                self._dirty = True

    def build(self):
        self._sorted = sorted(self._index.items(), key=lambda item: item[0])
        self._dirty = False
        logger.info(f"Built search index with {len(self._sorted)} words")

    def find(self, term: str, exact=False) -> Set[str]:
        if self._dirty:
            self.build()
        if exact:
            result = self._find_exact(term)
            return result if result else set()
        else:
            matches_for_term = self._find_startswith(term)
            return set.union(matches_for_term) if matches_for_term else set()

    def _find_exact(self, term):
        low = 0
        high = len(self._sorted) - 1
        while low <= high:
            pos = (low + high) // 2
            if self._sorted[pos][0] == term:
                return self._sorted[pos][1]
            if term < self._sorted[pos][0]:
                high = pos - 1
            else:
                low = pos + 1
        return set()

    def _find_startswith(self, term):
        results = set()
        low = 0
        high = len(self._sorted) - 1
        while low < high:
            pos = (low + high) // 2
            if self._sorted[pos][0] < term:
                low = pos + 1
            elif self._sorted[pos][0] > term:
                high = pos - 1
            else:
                low = pos
                break
        if low + 1 < len(self._sorted) and not self._sorted[low][0].startswith(term):
            low += 1
        while low < len(self._sorted) and self._sorted[low][0].startswith(term):
            results |= self._sorted[low][1]
            low += 1
        return results
