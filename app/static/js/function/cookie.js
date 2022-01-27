// 管理全局页面的cookie
// 当前项目设置

function set_current_project(id){
    localStorage["current_project_id"]=id;
}
function get_current_project_id(){
    return  localStorage["current_project_id"];
}