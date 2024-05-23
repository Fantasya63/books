$(function(){
    
    $('#inc-quantity-btn').click(function(){
        let val = $('#quantity-input').val();

        let new_val = parseInt($('#quantity-input').val(),10) + 1 ;
        if (new_val > 99 || new_val < 1)
            return;
        
        $('#quantity-input').val(new_val);
    });

    $('#dec-quantity-btn').click(function(){
        let val = $('#quantity-input').val();

        let new_val = parseInt($('#quantity-input').val(),10) - 1 ;
        if (new_val > 99 || new_val < 1)
            return;

        $('#quantity-input').val(new_val);
    });

});

