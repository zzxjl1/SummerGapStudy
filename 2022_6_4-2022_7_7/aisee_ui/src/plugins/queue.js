class Queue {
  constructor() {
    this.count = 0; //记录队列的数量
    this.lowestCount = 0; //记录当前队列顶部的位置
    this.items = []; //用来存储元素。
  }
  enqueue(element) {
    this.items[this.count] = element;
    this.count++;
  }
  dequeue() {
    if (this.isEmpty()) {
      return;
    }
    let resulte = this.items[this.lowestCount];
    //delete this.items[this.lowestCount];
    this.lowestCount++;
    return resulte;
  }
  back() {
    if (this.lowestCount == 0) return false;
    this.lowestCount--;
    return true;
  }
  front() {
    return this.items[this.lowestCount];
  }
  front_n(n) {
    var t = [];
    for (var i = 0; i < n; i++) {
      var item = this.items[this.lowestCount + i];
      if (item == undefined) break;
      t.push(item);
    }
    return t;
  }
  isEmpty() {
    return this.count - this.lowestCount === 0;
  }
  size() {
    return this.count - this.lowestCount;
  }
  clear() {
    this.count = 0;
    this.lowestCount = 0;
    this.items = [];
  }
  toString() {
    if (this.isEmpty()) return "queue is null";
    let objString = this.items[this.lowestCount];
    for (let i = this.lowestCount + 1; i < this.count; i++) {
      objString = `${objString},${this.items[i]}`;
    }
    return objString;
  }
}

module.exports = new Queue();
