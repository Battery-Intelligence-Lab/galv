"use strict";
goog.module('datarange');
goog.module.declareLegacyNamespace();

goog.require('proto.galvanalyser.DataRange');
goog.require('proto.galvanalyser.DataRanges');
goog.require('goog.structs.AvlTree');

class DataRange {
    constructor(start_sample_no, data_values) {
        this.from = start_sample_no;
        this.to = start_sample_no + data_values.length;
        this.data_values = data_values;
    }

    /**
     * Extend this data range with the values of another overlapping data range.
     * @param {DataRange} other_datarange 
     */
    extend_from(other_datarange){
        let lower, upper;
        if(this.from < other_datarange.from){
            lower = this;
            upper = other_datarange;
        } else {
            lower = other_datarange;
            upper = this;
        }
        if(lower.to > upper.to){
            //lower encompasses upper, set this to lower and return
            this.from = lower.from;
            this.to = lower.to;
            this.data_values = lower.data_values;
            return;
        }
        let start = lower.from;
        let end = upper.to;
        let data = lower.data_values.concat(upper.data_values.slice(lower.to - upper.from))
        this.from = start;
        this.to = end;
        this.data_values = data;
    }
}

function data_range_comp(a, b) {
    if(a instanceof DataRange){
        if(b instanceof DataRange){
            if(a.from > b.to){
                return 1;
            } else if( b.from > a.to){
                return -1;
            } else {
                return 0;
            }
        } else {
            // assume number if not DataRange
            if(a.from > b){
                return 1;
            } else if (a.to < b){
                return -1;
            } else {
                return 0;
            }
        }
    } else {
        if(b instanceof DataRange){
            if( a > b.to){
                return 1;
            } else if (a < b.from){
                return -1;
            } else {
                return 0;
            }
        } else {
            // They are both numbers, shouldn't happen
            return b - a;
        }
    }
}

class ReadingData {
    constructor(column_name) {
        this.column = column_name;
        this.tree = new goog.structs.AvlTree(data_range_comp);
    }

    add_data_range(data_range){
        while(this.tree.contains(data_range)){
            // merge data ranges first
            let existing_range = this.tree.remove(data_range);
            data_range.extend_from(existing_range);
        }
        this.tree.add(data_range);
    }

    get_readings_between(sample_no_from, sample_no_to){
        let data = new Array(0);
        this.tree.reverseOrderTraverse(function(data_range){
            let sample_no_end = Math.min(sample_no_to, data_range.to);
            let sample_no_start = Math.max(sample_no_from, data_range.from);
            let index_start = sample_no_start - data_range.from;
            let index_end = sample_no_end - data_range.from;
            let subset = data_range.data_values.slice(index_start, index_end);
            data = subset.concat(data);
            // stop iteration condition
            return (data_range.from <= sample_no_from );
        },
        sample_no_to);
        return data;
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

    add_protobuf_data_range(pb_data_range){
        let start_sample_no = pb_data_range.getStartSampleNo();
        for(const column_name of this.columns){
            let data = pb_data_range[`get${column_name}List`]();
            if(data.length >0){
                this[column_name].add_data_range(new DataRange(start_sample_no, data));
            }
        }
    }
}

exports.DataRange = DataRange;
exports.ExperimentData = ExperimentData;