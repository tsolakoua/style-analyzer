import lzma
from pathlib import Path
import unittest

import bblfsh
from sklearn import model_selection, tree

from lookout.core.api.service_data_pb2 import File
from lookout.style.format.features import FeatureExtractor
from lookout.style.format.rules import TrainableRules


class RulesIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = Path(__file__).parent
        # str() is needed for Python 3.5
        with lzma.open(str(base / "benchmark.js.xz"), mode="rt") as fin:
            contents = fin.read()
        with lzma.open(str(base / "benchmark.uast.xz")) as fin:
            uast = bblfsh.Node.FromString(fin.read())
        file = File(content=bytes(contents, "utf-8"),
                    uast=uast)
        cls.files = [file]
        cls.extractor = FeatureExtractor("javascript",
                                         parents_depth=2,
                                         siblings_window=5)

    def test_integration(self):
        X, y, _ = self.extractor.extract_features(self.files)
        train_X, test_X, train_y, test_y = \
            model_selection.train_test_split(X, y, random_state=1989)

        model = tree.DecisionTreeClassifier(min_samples_leaf=26, random_state=1989, max_depth=None,
                                            max_features="auto", min_samples_split=2)
        model.fit(train_X, train_y)
        rules = TrainableRules("sklearn.tree.DecisionTreeClassifier", prune_branches_algorithms=[],
                               prune_attributes=False, min_samples_leaf=26, random_state=1989,
                               max_depth=None, max_features="auto", min_samples_split=2)
        rules.fit(train_X, train_y)
        model_score_train = model.score(train_X, train_y)
        model_score_test = model.score(test_X, test_y)
        rules_score_train = rules.score(train_X, train_y)
        rules_score_test = rules.score(test_X, test_y)
        self.assertEqual(rules_score_train, model_score_train)
        self.assertEqual(rules_score_test, model_score_test)


if __name__ == "__main__":
    unittest.main()
