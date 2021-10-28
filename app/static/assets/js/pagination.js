function Pagination(url, column_names, tb_id, widget_id, name,color,td_color,front_color) {
    this.url = url;
    this.tb_id = tb_id;
    this.column_names = column_names;
    this.widget_id = widget_id;
    this.name = name;
    this.data = Object();
    this.btn = [];
    this.color = color;
    this.td_color = td_color;
    this.front_colot = front_color;

    this.setBtn = function (btn_list) {
        this.btn = btn_list;
    }

    this.setData = function (data) {
        this.data = data
    };
    this.cleanData = function () {
        this.data = Object();
    };

    this.turnPage = function (page) {
        var _this = this;
        url = _this.changeURLArg(_this.url, 'page', page.toString());
        $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify(_this.data),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            success: function (data) {
                _this.refreshTbody(data.items);
                var widget = new Widget(data.widget, _this.widget_id, _this);
                widget.refreshWidget();
            },
            error: function (xhr) {
                console.error('error');
            }
        });
    };

    this.refreshTbody = function (items) {
        var _tb = document.getElementById(this.tb_id);
        var _tbody = _tb.getElementsByTagName('tbody')[0];
        _tbody.textContent = '';
        for (var i = 0; i < items.length; i++) {
            var _tb = this.createTr(items[i]);
            _tbody.appendChild(_tb);
        }
    };

    this.createTr = function (item) {
        var _tr = document.createElement('tr');
        _tr.className = 'gradeX';
        for (var i = 0; i < this.column_names.length; i++) {
            if (this.btn.indexOf(this.column_names[i]) === -1) {
                if(item['abnormals'].indexOf(this.column_names[i])>-1) {
                    this.addTd(_tr, item[this.column_names[i]],false,this.color);
                }
                else{
                    this.addTd(_tr, item[this.column_names[i]],false,false);
                }

            }
            else {
                 if(item[abnormals].indexOf(this.column_names[i])) {
                    this.addTd(_tr, item[this.column_names[i]],true,this.color);
                }
                else{
                    this.addTd(_tr, item[this.column_names[i]],true,false);
                }
            }

        }
        return _tr;
    };

    this.addTd = function (_tr, value, btn,color) {
        var btn = arguments[2] ? arguments[2] : false;
        _td = document.createElement('td');
        if (btn) {
            _td.innerHTML = value;
        }
        else {
            _td.textContent = value;
        }
        if (color){
            _td.style.backgroundColor=this.td_color;
            _td.style.color=this.front_colot;
        }
        _tr.appendChild(_td);
    };

    this.changeURLArg = function (url, arg, arg_val) {
        var pattern = arg + '=([^&]*)';
        var replaceText = arg + '=' + arg_val;
        if (url.match(pattern)) {
            var tmp = '/(' + arg + '=)([^&]*)/gi';
            tmp = url.replace(eval(tmp), replaceText);
            return tmp;
        } else {
            if (url.match('[\?]')) {
                return url + '&' + replaceText;
            } else {
                return url + '?' + replaceText;
            }
        }
        return url + '\n' + arg + '\n' + arg_val;
    }
};

function Widget(_widget, widget_id, pag) {
    this.page = _widget.page;
    this.has_prev = _widget.has_prev;
    this.prev_num = _widget.prev_num;
    this.pages = _widget.pages;
    this.has_next = _widget.has_next;
    this.next_num = _widget.next_num;
    this.enough_page = _widget.enough_page;
    this.widget_id = widget_id;
    this.pag = pag;

    this.createTaga = function (pag, page, text) {
        var a = document.createElement('a');
        a.textContent = text;
        if (page === '#') {
            return a;
        }
        if (page === '…') {
            a.textContent = '…';
            return a;
        }
        else {
            a.onclick = function () {
                pag.turnPage(page);
            };
        }
        return a;
    };

    this.refreshWidget = function () {
        var _widget_div = document.getElementById(this.widget_id);
        _widget_div.textContent = '';
        var ul = document.createElement('ul');
        ul.className = 'pagination';
        var prev = document.createElement('li');
        var prev_a = this.has_prev ? this.createTaga(this.pag, this.prev_num, '«') : this.createTaga(this.pag, '#', '«');
        prev.appendChild(prev_a);
        ul.appendChild(prev);
        if (this.pages.length < 9) {
            // for (i = this.pages.length - 2; i < this.pages.length + 3; i++) {
            for (i = 0; i < this.pages.length; i++) {
                var _li = document.createElement('li');
                var _li_a = null;
                if (this.pages[i] === this.page) {
                    _li_a = this.createTaga(this.pag, '#', this.pages[i]);
                    _li.className = "active";
                }
                else {
                    _li_a = this.createTaga(this.pag, this.pages[i], this.pages[i]);
                }
                _li.appendChild(_li_a);
                ul.appendChild(_li);
            }
        }
        else {
            var new_pages = [1, 2, this.page - 2, this.page - 1, this.page, this.page + 1, this.page + 2, '…', this.pages[this.pages.length - 2], this.pages[this.pages.length - 1]];
            var tmp = [];
            for (var i = 0; i < new_pages.length; i++) {
                if (new_pages[i] <= 0 || tmp.indexOf(new_pages[i]) >= 0 || new_pages[i] > this.pages.length) {
                    continue;
                }
                tmp.push(new_pages[i]);
                var _li = document.createElement('li');
                if (new_pages[i] === this.page) {
                    var _li_a = this.createTaga(this.pag, '#', new_pages[i]);
                    _li.className = "active";
                }
                else {
                    var _li_a = this.createTaga(this.pag, new_pages[i], new_pages[i]);
                }

                _li.appendChild(_li_a);
                ul.appendChild(_li);
            }
        }
        var next = document.createElement('li');
        var next_a = this.has_next ? this.createTaga(this.pag, this.next_num, '»') : this.createTaga(this.pag, '#', '»');
        next.appendChild(next_a);
        ul.appendChild(next);
        _widget_div.appendChild(ul);
    };
}