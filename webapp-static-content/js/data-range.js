"use strict";
goog.module('datarange');
goog.module.declareLegacyNamespace();

goog.require('proto.galvanalyser.DataRange');
goog.require('proto.galvanalyser.DataRanges');
goog.require('goog.structs.AvlTree');

class DataRange {
    constructor(data_indicies, data_values) {
        this.from = 0;
        this.to = 1;
    }
}

function data_range_comp(a, b) {
    return b.from - a.from;
}

class ReadingData {
    constructor(column_name) {
        this.column = column_name;
        this.tree = new goog.structs.AvlTree(data_range_comp);
    }

}

class ExperimentData {

    constructor() {
        let temp_pb = new proto.galvanalyser.DataRange();
        let list_regex = /get(\w+)List/;
        this.columns = [];
        for (const prop in temp_pb) {
            if (!temp_pb.hasOwnProperty(prop)) {
                let match = list_regex.exec(prop);
                if (match && match[1]) {
                    let column = match[1];
                    this[column] = new ReadingData(column);
                    this.columns.push(column);
                    //console.log(`obj.${prop} = ${temp_pb[prop]}`);
                }
            }
        }
    }
}

exports.DataRange = DataRange;
exports.ExperimentData = ExperimentData;