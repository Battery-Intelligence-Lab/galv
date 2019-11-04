"use strict";
goog.module('datarange');
goog.module.declareLegacyNamespace();

goog.require('proto.galvanalyser.DataRange');
goog.require('proto.galvanalyser.DataRanges');
goog.require('goog.structs.AvlTree');

class DataRange {
    constructor(start_sample_no, data_values) {
        this.from = start_sample_no;
        if (typeof data_values == 'number') {
            // data_values can also be the end sample no 
            this.to = data_values;
            this.data_values = [];
        } else {
            this.to = start_sample_no + data_values.length;
            this.data_values = data_values;
        }
    }

    /**
     * Extend this data range with the values of another overlapping data range.
     * @param {DataRange} other_datarange 
     */
    extend_from(other_datarange) {
        let lower, upper;
        if (this.from < other_datarange.from) {
            lower = this;
            upper = other_datarange;
        } else {
            lower = other_datarange;
            upper = this;
        }
        if (lower.to > upper.to) {
            //lower encompasses upper, set this to lower and return
            this.from = lower.from;
            this.to = lower.to;
            this.data_values = lower.data_values;
            return;
        }
        let start = lower.from;
        let end = upper.to;
        let data = lower.data_values.concat(upper.data_values.slice(lower.to - upper.from));
        this.from = start;
        this.to = end;
        this.data_values = data;
    }

    get_subset(sample_no_from, sample_no_to) {
        if (sample_no_from == this.from && sample_no_to == this.to) {
            return this;
        }
        let sample_no_end = Math.min(sample_no_to, this.to);
        let sample_no_start = Math.max(sample_no_from, this.from);
        let index_start = sample_no_start - this.from;
        let index_end = sample_no_end - this.from;
        let subset = this.data_values.slice(index_start, index_end);
        return new DataRange(sample_no_start, subset);
    }

}

function data_range_comp(a, b) {
    if (a instanceof DataRange) {
        if (b instanceof DataRange) {
            if (a.from > b.to) {
                return 1;
            } else if (b.from > a.to) {
                return -1;
            } else {
                return 0;
            }
        } else {
            // assume number if not DataRange
            if (a.from > b) {
                return 1;
            } else if (a.to < b) {
                return -1;
            } else {
                return 0;
            }
        }
    } else {
        if (b instanceof DataRange) {
            if (a > b.to) {
                return 1;
            } else if (a < b.from) {
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
    constructor(column_id) {
        this.column_id = column_id;
        this.tree = new goog.structs.AvlTree(data_range_comp);
    }

    add_data_range(data_range) {
        while (this.tree.contains(data_range)) {
            // merge data ranges first
            let existing_range = this.tree.remove(data_range);
            data_range.extend_from(existing_range);
        }
        this.tree.add(data_range);
    }

    get_readings_between(sample_no_from, sample_no_to) {
        let data = new Array(0);
        this.tree.reverseOrderTraverse(function(data_range) {
                let datarange_subset = data_range.get_subset(sample_no_from, sample_no_to);
                //let sample_no_end = Math.min(sample_no_to, data_range.to);
                //let sample_no_start = Math.max(sample_no_from, data_range.from);
                //let index_start = sample_no_start - data_range.from;
                //let index_end = sample_no_end - data_range.from;
                //let subset = data_range.data_values.slice(index_start, index_end);
                data = datarange_subset.data_values.concat(data);
                // stop iteration condition
                return (data_range.from <= sample_no_from);
            },
            sample_no_to);
        return data;
    }

    get_ranges_between(sample_no_from, sample_no_to) {
        let results = [];
        this.tree.reverseOrderTraverse(function(data_range) {
                if (data_range.to > sample_no_to || data_range.from < sample_no_from) {
                    //this is an end block, make a new datarange from the partial block
                    results.push(data_range.get_subset(sample_no_from, sample_no_to));
                } else {
                    // this block is wholly contained in the requested range
                    results.push(data_range);
                }
                // stop iteration condition
                return (data_range.from <= sample_no_from);
            },
            sample_no_to);
        results.reverse();
        return results;
    }

    iterate_ranges(func) {
        this.tree.inOrderTraverse(func);
    }
    iterate_ranges_from(func, start_sample_no) {
        this.tree.inOrderTraverse(func, start_sample_no);
    }

}

class DatasetData {

    constructor() {
        this.columns = new Map();
    }

    add_protobuf_data_range(column_id, pb_data_range) {
        if (!this.columns.has(column_id)) {
            this.columns.set(column_id, new ReadingData(column_id));
        }
        let reading_data = this.columns.get(column_id);
        let start_sample_no = pb_data_range.getStartSampleNo();
        let data = pb_data_range.getValuesList();
        if (data.length > 0) {
            reading_data.add_data_range(new DataRange(start_sample_no, data));
        }
    }

    add_empty_data_range(column_id, start_sample_no, end_sample_no) {
        if (!this.columns.has(column_id)) {
            this.columns.set(column_id, new ReadingData(column_id));
        }
        let reading_data = this.columns.get(column_id);
        reading_data.add_data_range(new DataRange(start_sample_no, end_sample_no));
    }
}

exports.DataRange = DataRange;
exports.DatasetData = DatasetData;