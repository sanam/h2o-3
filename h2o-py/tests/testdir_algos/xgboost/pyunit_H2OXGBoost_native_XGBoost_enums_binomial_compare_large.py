import xgboost as xgb
import time
import random

from h2o.estimators.xgboost import *
from tests import pyunit_utils

'''
The goal of this test is to compare the results of H2OXGBoost and natibve XGBoost for binomial classification.
The dataset contains only enum columns.
'''
def comparison_test():
    assert H2OXGBoostEstimator.available() is True
    runSeed = random.randint(1, 1073741824)
    ntrees = 10
    h2oParamsD = {"ntrees":ntrees, "max_depth":4, "seed":runSeed, "learn_rate":0.7, "col_sample_rate_per_tree" : 0.9,
                 "min_rows" : 5, "score_tree_interval": ntrees+1, "dmatrix_type":"dense"}
    h2oParamsS = {"ntrees":ntrees, "max_depth":4, "seed":runSeed, "learn_rate":0.7, "col_sample_rate_per_tree" : 0.9,
                  "min_rows" : 5, "score_tree_interval": ntrees+1, "dmatrix_type":"sparse"}
    nativeParam = {'colsample_bytree': h2oParamsD["col_sample_rate_per_tree"],
                   'tree_method': 'auto',
                   'seed': h2oParamsD["seed"],
                   'booster': 'gbtree',
                   'objective': 'binary:logistic',
                   'lambda': 0.0,
                   'eta': h2oParamsD["learn_rate"],
                   'grow_policy': 'depthwise',
                   'alpha': 0.0,
                   'subsample': 1.0,
                   'colsample_bylevel': 1.0,
                   'max_delta_step': 0.0,
                   'min_child_weight': h2oParamsD["min_rows"],
                   'gamma': 0.0,
                   'max_depth': h2oParamsD["max_depth"]}

    nrows = 100000
    ncols = 10
    factorL = 10

    trainFile = pyunit_utils.genTrainFiles(nrows, 0, enumCols=ncols, enumFactors=factorL)     # load in dataset and add response column
    myX = trainFile.names
    y='response'
    myX.remove(y)

    h2oModelD = H2OXGBoostEstimator(**h2oParamsD)
    # gather, print and save performance numbers for h2o model
    h2oModelD.train(x=myX, y=y, training_frame=trainFile)
    h2oTrainTimeD = h2oModelD._model_json["output"]["run_time"]
    time1 = time.time()
    h2oPredictD = h2oModelD.predict(trainFile)
    h2oPredictTimeD = time.time()-time1

    h2oModelS = H2OXGBoostEstimator(**h2oParamsS)
    # gather, print and save performance numbers for h2o model
    h2oModelS.train(x=myX, y=y, training_frame=trainFile)
    h2oTrainTimeS = h2oModelS._model_json["output"]["run_time"]
    time1 = time.time()
    h2oPredictS = h2oModelS.predict(trainFile)
    h2oPredictTimeS = time.time()-time1

    print("H2OXGBoost train time with sparse DMatrix is {0}ms.  H2OXGBoost train time with dense DMatrix is {1}ms\n.  H2OGBoost scoring time with sparse DMatrix is {2}s."
          "  H2OGBoost scoring time with dense DMatrix is {3}s..".format(h2oTrainTimeS, h2oTrainTimeD,
                                                                             h2oPredictTimeS, h2oPredictTimeD))

    # train the native XGBoost
    nativeTrain = pyunit_utils.genDMatrix(trainFile, myX, y, myX)
    nativeModel = xgb.train(params=nativeParam,
                            dtrain=nativeTrain)
    nativeTrainTime = time.time()-time1
    time1=time.time()
    nativePred = nativeModel.predict(data=nativeTrain, ntree_limit=ntrees)
    nativeScoreTime = time.time()-time1

    pyunit_utils.summarizeResult_binomial_DS(h2oPredictD, nativePred, h2oTrainTimeD, nativeTrainTime, h2oPredictTimeD,
                                 nativeScoreTime, h2oPredictS, tolerance=1e-4)


if __name__ == "__main__":
    pyunit_utils.standalone_test(comparison_test)
else:
    comparison_test()
