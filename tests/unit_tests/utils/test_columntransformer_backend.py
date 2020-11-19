"""
Unit test of Inverse Transform
"""
import unittest
import pandas as pd
import category_encoders as ce
from sklearn.compose import ColumnTransformer
import sklearn.preprocessing as skp
import catboost as cb
import sklearn
import lightgbm
import xgboost
from shapash.utils.transform import inverse_transform, apply_preprocessing


# TODO
# StandardScaler return object vs float vs int
# Target encoding return object vs float

class TestInverseTransformColumnsTransformer(unittest.TestCase):
    def test_inverse_multiple_ct_drop(self):
        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']},
                             index=['index1', 'index2'])

        enc = ColumnTransformer(
            transformers=[
                ('onehot_ce', ce.OneHotEncoder(), ['city', 'state']),
                ('onehot_skp', skp.OneHotEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']},
                            index=['index1', 'index2', 'index3'])

        expected = pd.DataFrame({'onehot_ce_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_ce_state': ['US', 'FR', 'FR'],
                                 'onehot_skp_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_skp_state': ['US', 'FR', 'FR']},
                                index=['index1', 'index2', 'index3'])

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1', 'col3_0', 'col3_1', 'col4_0', 'col4_1']
        result.index = ['index1', 'index2', 'index3']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_multiple_ct_passthrough(self):
        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']},
                             index=['index1', 'index2'])

        enc = ColumnTransformer(
            transformers=[
                ('onehot_ce', ce.OneHotEncoder(), ['city', 'state']),
                ('onehot_skp', skp.OneHotEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')
        enc.fit(train)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']},
                            index=['index1', 'index2', 'index3'])

        expected = pd.DataFrame({'onehot_ce_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_ce_state': ['US', 'FR', 'FR'],
                                 'onehot_skp_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_skp_state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']},
                                index=['index1', 'index2', 'index3'])

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1', 'col3_0', 'col3_1', 'col4_0', 'col4_1', 'other']
        result.index = ['index1', 'index2', 'index3']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_multiple_ct_dict(self):
        train = pd.DataFrame({'city': ['chicago', 'paris'],
                                  'state': ['US', 'FR'],
                                  'other': ['A', 'B']},
                                 index=['index1', 'index2'])

        enc = ColumnTransformer(
                transformers=[
                    ('onehot_ce', ce.OneHotEncoder(), ['city', 'state']),
                    ('onehot_skp', skp.OneHotEncoder(), ['city', 'state'])
                ],
                remainder='passthrough')
        enc.fit(train)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                                 'state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']},
                                index=['index1', 'index2', 'index3'])

        expected = pd.DataFrame({'onehot_ce_city': ['CH', 'CH', 'PR'],
                                     'onehot_ce_state': ['US-FR', 'US-FR', 'US-FR'],
                                     'onehot_skp_city': ['chicago', 'chicago', 'paris'],
                                     'onehot_skp_state': ['US', 'FR', 'FR'],
                                     'other': ['A-B', 'A-B', 'C']},
                                    index=['index1', 'index2', 'index3'])

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1', 'col3_0', 'col3_1', 'col4_0', 'col4_1', 'other']
        result.index = ['index1', 'index2', 'index3']

        input_dict1 = dict()
        input_dict1['col'] = 'onehot_ce_city'
        input_dict1['mapping'] = pd.Series(data=['chicago', 'paris'], index=['CH', 'PR'])
        input_dict1['data_type'] = 'object'

        input_dict2 = dict()
        input_dict2['col'] = 'other'
        input_dict2['mapping'] = pd.Series(data=['A', 'B', 'C'], index=['A-B', 'A-B', 'C'])
        input_dict2['data_type'] = 'object'

        input_dict3 = dict()
        input_dict3['col'] = 'onehot_ce_state'
        input_dict3['mapping'] = pd.Series(data=['US', 'FR'], index=['US-FR', 'US-FR'])
        input_dict3['data_type'] = 'object'
        list_dict = [input_dict2, input_dict3]

        original = inverse_transform(result, [enc,input_dict1,list_dict])
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_target_passthrough(self):
        y = pd.DataFrame(data=[0, 1, 1, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris', 'paris', 'chicago'],
                              'state': ['US', 'FR', 'FR', 'US'],
                              'other': ['A', 'B', 'B', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('target', ce.TargetEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')

        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame(data={'target_city': ['chicago', 'chicago', 'paris'],
                                      'target_state': ['US', 'FR', 'FR'],
                                      'other': ['A', 'B', 'C']},
                                dtype=object)

        enc.fit(train, y)
        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_target_drop(self):
        y = pd.DataFrame(data=[0, 1, 0, 0], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris', 'chicago', 'paris'],
                              'state': ['US', 'FR', 'US', 'FR'],
                              'other': ['A', 'B', 'A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('target', ce.TargetEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame(data={
                    'target_city': ['chicago', 'chicago', 'paris'],
                    'target_state': ['US', 'FR', 'FR']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_OrdinalEncoder_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('ordinal', ce.OrdinalEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train, y)

        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'ordinal_city': ['chicago', 'chicago', 'paris'],
                                 'ordinal_state': ['US', 'FR', 'FR']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_OrdinalEncoder_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('ordinal', ce.OrdinalEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'ordinal_city': ['chicago', 'chicago', 'paris'],
                                 'ordinal_state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_Binary_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('binary', ce.BinaryEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train, y)

        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'binary_city': ['chicago', 'chicago', 'paris'],
                                 'binary_state': ['US', 'FR', 'FR']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_Binary_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('binary', ce.BinaryEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'binary_city': ['chicago', 'chicago', 'paris'],
                                 'binary_state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_BaseN_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('basen', ce.BaseNEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'basen_city': ['chicago', 'chicago', 'paris'],
                                 'basen_state': ['US', 'FR', 'FR']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_BaseN_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('basen', ce.BaseNEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'basen_city': ['chicago', 'chicago', 'paris'],
                                 'basen_state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_onehot_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('onehot', ce.OneHotEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'onehot_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_state': ['US', 'FR', 'FR']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_ce_onehot_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('onehot', ce.OneHotEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'onehot_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_onehot_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('onehot', skp.OneHotEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'onehot_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_state': ['US', 'FR', 'FR']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_onehot_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('onehot', skp.OneHotEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'onehot_city': ['chicago', 'chicago', 'paris'],
                                 'onehot_state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1_0', 'col1_1', 'col2_0', 'col2_1', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_ordinal_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('ordinal', skp.OrdinalEncoder(), ['city', 'state'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'ordinal_city': ['chicago', 'chicago', 'paris'],
                                 'ordinal_state': ['US', 'FR', 'FR']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_ordinal_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'city': ['chicago', 'paris'],
                              'state': ['US', 'FR'],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('ordinal', skp.OrdinalEncoder(), ['city', 'state'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'city': ['chicago', 'chicago', 'paris'],
                             'state': ['US', 'FR', 'FR'],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'ordinal_city': ['chicago', 'chicago', 'paris'],
                                 'ordinal_state': ['US', 'FR', 'FR'],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_standardscaler_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('std', skp.StandardScaler(), ['num1', 'num2'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'std_num1': [0.0, 1.0, 1.0],
                                 'std_num2': [0.0, 2.0, 3.0],
                                 'other': ['A', 'B', 'C']},
                                dtype=object)

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_standardscaler_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('std', skp.StandardScaler(), ['num1', 'num2'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'std_num1': [0.0, 1.0, 1.0],
                                 'std_num2': [0.0, 2.0, 3.0]})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_quantile_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('quantile', skp.QuantileTransformer(n_quantiles=2), ['num1', 'num2'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'quantile_num1': [0.0, 1.0, 1.0],
                                 'quantile_num2': [0.0, 2.0, 2.0],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_quantile_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('quantile', skp.QuantileTransformer(n_quantiles=2), ['num1', 'num2'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'quantile_num1': [0.0, 1.0, 1.0],
                                 'quantile_num2': [0.0, 2.0, 2.0]})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_power_passthrough(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('power', skp.PowerTransformer(), ['num1', 'num2'])
            ],
            remainder='passthrough')
        enc.fit(train, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'power_num1': [0.0, 1.0, 1.0],
                                 'power_num2': [0.0, 1.9999999997665876, 3.000000000169985],
                                 'other': ['A', 'B', 'C']})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2', 'other']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_inverse_single_skp_power_drop(self):
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(
            transformers=[
                ('power', skp.QuantileTransformer(n_quantiles=2), ['num1', 'num2'])
            ],
            remainder='drop')
        enc.fit(train, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame({'power_num1': [0.0, 1.0, 1.0],
                                 'power_num2': [0.0, 2.0, 2.0]})

        result = pd.DataFrame(enc.transform(test))
        result.columns = ['col1', 'col2']
        original = inverse_transform(result, enc)
        pd.testing.assert_frame_equal(original, expected)

    def test_transform_ct_1(self):
        """
        Unit test for apply_preprocessing on ColumnTransformer with drop option and sklearn encoder.
        """
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': ['A', 'B']})

        enc = ColumnTransformer(transformers=[('power', skp.QuantileTransformer(n_quantiles=2), ['num1', 'num2'])],
                                remainder='drop')
        enc.fit(train, y)

        train_preprocessed = pd.DataFrame(enc.transform(train))

        clf = cb.CatBoostClassifier(n_estimators=1).fit(train_preprocessed, y)

        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': ['A', 'B', 'C']})

        expected = pd.DataFrame(enc.transform(test))
        result = apply_preprocessing(test, clf, enc)
        assert result.shape == expected.shape
        assert [column in clf.feature_names_ for column in result.columns]
        assert all(expected.index == result.index)
        assert all([str(type_result) == str(expected.dtypes[index])
                    for index, type_result in enumerate(result.dtypes)])

    def test_transform_ct_2(self):
        """
        Unit test for apply_preprocessing on ColumnTransformer with passthrough option and category encoder.
        """
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': [1, 0]})

        enc = ColumnTransformer(transformers=[('onehot_ce', ce.OneHotEncoder(), ['num1', 'num2'])],
                                remainder='passthrough')
        enc.fit(train, y)

        train_preprocessed = pd.DataFrame(enc.transform(train))
        clf = cb.CatBoostClassifier(n_estimators=1).fit(train_preprocessed, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 3],
                             'other': [1, 0, 3]})

        expected = pd.DataFrame(enc.transform(test))
        result = apply_preprocessing(test, clf, enc)
        assert result.shape == expected.shape
        assert [column in clf.feature_names_ for column in result.columns]
        assert all(expected.index == result.index)
        assert all([str(type_result) == str(expected.dtypes[index])
                    for index, type_result in enumerate(result.dtypes)])

    def test_transform_ct_3(self):
        """
        Unit test for apply_preprocessing on ColumnTransformer with sklearn encoder and category encoder.
        """
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': [1, 0]})

        enc = ColumnTransformer(transformers=[('onehot_ce', ce.OneHotEncoder(), ['num1', 'num2']),
                                              ('onehot_skp', skp.OneHotEncoder(), ['num1', 'num2'])],
                                remainder='passthrough')
        enc.fit(train, y)

        train_preprocessed = pd.DataFrame(enc.transform(train))
        clf = cb.CatBoostClassifier(n_estimators=1).fit(train_preprocessed, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 0],
                             'other': [1, 0, 0]})

        expected = pd.DataFrame(enc.transform(test), index=test.index)
        result = apply_preprocessing(test, clf, enc)
        assert result.shape == expected.shape
        assert [column in clf.feature_names_ for column in result.columns]
        assert all(expected.index == result.index)

    def test_transform_ct_4(self):
        """
        Unit test for apply_preprocessing on list of a dict, a list of dict and a ColumnTransformer.
        """
        train = pd.DataFrame({'city': ['CH', 'CH', 'PR'],
                              'state': ['US-FR', 'US-FR', 'US-FR'],
                              'other': ['A-B', 'A-B', 'C']},
                             index=['index1', 'index2', 'index3'])

        y = pd.DataFrame(data=[0, 1, 0], columns=['y'], index=['index1', 'index2', 'index3'])

        train_preprocessed = train.copy()
        input_dict1 = dict()
        input_dict1['col'] = 'city'
        input_dict1['mapping'] = pd.Series(data=['chicago', 'paris'], index=['CH', 'PR'])
        input_dict1['data_type'] = 'object'

        transform_input_1 = pd.Series(data=input_dict1.get("mapping").values, index=input_dict1.get("mapping").index)
        train_preprocessed[input_dict1.get("col")] = train_preprocessed[input_dict1.get("col")].map(
            transform_input_1).astype(input_dict1.get("mapping").values.dtype)

        input_dict2 = dict()
        input_dict2['col'] = 'other'
        input_dict2['mapping'] = pd.Series(data=['A', 'C'], index=['A-B', 'C'])
        input_dict2['data_type'] = 'object'

        transform_input_2 = pd.Series(data=input_dict2.get("mapping").values, index=input_dict2.get("mapping").index)
        train_preprocessed[input_dict2.get("col")] = train_preprocessed[input_dict2.get("col")].map(
            transform_input_2).astype(input_dict2.get("mapping").values.dtype)

        input_dict3 = dict()
        input_dict3['col'] = 'state'
        input_dict3['mapping'] = pd.Series(data=['US FR'], index=['US-FR'])
        input_dict3['data_type'] = 'object'

        transform_input_3 = pd.Series(data=input_dict3.get("mapping").values, index=input_dict3.get("mapping").index)
        train_preprocessed[input_dict3.get("col")] = train_preprocessed[input_dict3.get("col")].map(
            transform_input_3).astype(input_dict3.get("mapping").values.dtype)

        enc = ColumnTransformer(
            transformers=[
                ('onehot_ce', ce.OneHotEncoder(), ['city', 'state']),
                ('onehot_skp', skp.OneHotEncoder(), ['other'])
            ],
            remainder='passthrough')

        enc.fit(train_preprocessed)
        train_preprocessed = pd.DataFrame(enc.transform(train_preprocessed), index=train.index)
        train_preprocessed.columns = [str(feature) for feature in train_preprocessed.columns]

        clf = cb.CatBoostClassifier(n_estimators=1).fit(train_preprocessed, y)

        list_dict = [input_dict2, input_dict3]

        test_preprocessing = apply_preprocessing(train, clf, [input_dict1, list_dict, enc])
        pd.testing.assert_frame_equal(train_preprocessed, test_preprocessing)

    def test_transform_ct_5(self):
        """
        Unit test for apply_preprocessing with ColumnTransformer and sklearn model.
        """
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': [1, 0]})

        enc = ColumnTransformer(transformers=[('onehot_ce', ce.OneHotEncoder(), ['num1', 'num2']),
                                              ('onehot_skp', skp.OneHotEncoder(), ['num1', 'num2'])],
                                remainder='passthrough')
        enc.fit(train, y)

        train_preprocessed = pd.DataFrame(enc.transform(train))
        clf = sklearn.ensemble._gb.GradientBoostingClassifier(n_estimators=1).fit(train_preprocessed, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 0],
                             'other': [1, 0, 0]})

        expected = pd.DataFrame(enc.transform(test), index=test.index)
        result = apply_preprocessing(test, clf, enc)
        assert result.shape == expected.shape
        assert all(expected.index == result.index)

    def test_transform_ct_6(self):
        """
        Unit test for apply_preprocessing with ColumnTransformer and catboost model.
        """
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': [1, 0]})

        enc = ColumnTransformer(transformers=[('onehot_ce', ce.OneHotEncoder(), ['num1', 'num2']),
                                              ('onehot_skp', skp.OneHotEncoder(), ['num1', 'num2'])],
                                remainder='passthrough')
        enc.fit(train, y)

        train_preprocessed = pd.DataFrame(enc.transform(train))
        clf = cb.CatBoostClassifier(n_estimators=1).fit(train_preprocessed, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 0],
                             'other': [1, 0, 0]})

        expected = pd.DataFrame(enc.transform(test), index=test.index)
        result = apply_preprocessing(test, clf, enc)
        assert result.shape == expected.shape
        assert [column in clf.feature_names_ for column in result.columns]
        assert all(expected.index == result.index)

    def test_transform_ct_7(self):
        """
        Unit test for apply_preprocessing with ColumnTransformer and lightgbm model.
        """
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': [1, 0]})

        enc = ColumnTransformer(transformers=[('onehot_ce', ce.OneHotEncoder(), ['num1', 'num2']),
                                              ('onehot_skp', skp.OneHotEncoder(), ['num1', 'num2'])],
                                remainder='passthrough')
        enc.fit(train, y)

        train_preprocessed = pd.DataFrame(enc.transform(train))
        clf = lightgbm.sklearn.LGBMClassifier(n_estimators=1).fit(train_preprocessed, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 0],
                             'other': [1, 0, 0]})

        expected = pd.DataFrame(enc.transform(test), index=test.index)
        result = apply_preprocessing(test, clf, enc)
        assert result.shape == expected.shape
        assert [column in clf.booster_.feature_name() for column in result.columns]
        assert all(expected.index == result.index)

    def test_transform_ct_8(self):
        """
        Unit test for apply_preprocessing with ColumnTransformer and xgboost model.
        """
        y = pd.DataFrame(data=[0, 1], columns=['y'])

        train = pd.DataFrame({'num1': [0, 1],
                              'num2': [0, 2],
                              'other': [1, 0]})

        enc = ColumnTransformer(transformers=[('onehot_ce', ce.OneHotEncoder(), ['num1', 'num2']),
                                              ('onehot_skp', skp.OneHotEncoder(), ['num1', 'num2'])],
                                remainder='passthrough')
        enc.fit(train, y)

        train_preprocessed = pd.DataFrame(enc.transform(train))
        clf = xgboost.sklearn.XGBClassifier(n_estimators=1).fit(train_preprocessed, y)
        test = pd.DataFrame({'num1': [0, 1, 1],
                             'num2': [0, 2, 0],
                             'other': [1, 0, 0]})

        expected = pd.DataFrame(enc.transform(test), index=test.index)
        result = apply_preprocessing(test, clf, enc)
        assert result.shape == expected.shape
        assert [column in clf.get_booster().feature_names for column in result.columns]
        assert all(expected.index == result.index)