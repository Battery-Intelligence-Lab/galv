"use strict";
goog.module('datarange');
goog.module.declareLegacyNamespace();

goog.require('goog.structs.AvlTree');

class DataRange{
    constructor(data_indicies, data_values){
        this.from = 0;
        this.to = 1;
    }
}

function data_range_comp(a, b){
    return b.from - a.from;
}

class ExperimentData{

    constructor(){
        this.tree = new goog.structs.AvlTree(data_range_comp);
    }
}

exports.DataRange = DataRange;
exports.ExperimentData = ExperimentData;