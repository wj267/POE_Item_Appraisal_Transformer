# POE_Item_Appraisal_Transformer
An amateur attempt at training a transformer to appraise rare items in path of exile using market data.


 - PTQ is a module which uses a provided JSON string specifying search filters to query the Path of Exile trade server for items in a given league in bcount batches of 10 items per batch.
 - TrainingDataPull is a script which pulls and cleans the data set to CSV. Removing superfluous data and splitting strings for tokenization.
 - BuildDataset was originally just going to build the dataset object, but has turned into the testbed where I'm trying to get the model to work.
