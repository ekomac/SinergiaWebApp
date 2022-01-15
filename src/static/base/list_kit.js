function orderByChanged(order_by, order_by_id, form_id, is_default = false) {
    const original_order_by = $('#' + order_by_id).val();
    if ((['', null, undefined].includes(original_order_by) && !is_default) || (original_order_by != order_by)) {
        $('#' + order_by_id).val(order_by);
        $('#' + form_id).submit();
    }
}