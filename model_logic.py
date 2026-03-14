def score(input):
    if input[3] <= 89.94999694824219:
        var0 = [0.0, 0.0, 1.0]
    else:
        if input[2] <= 14.900000095367432:
            var0 = [0.0, 0.0, 1.0]
        else:
            if input[5] <= 0.5:
                var0 = [1.0, 0.0, 0.0]
            else:
                if input[4] <= 0.5:
                    var0 = [1.0, 0.0, 0.0]
                else:
                    if input[6] <= 0.5:
                        var0 = [1.0, 0.0, 0.0]
                    else:
                        var0 = [0.0, 1.0, 0.0]
    return var0
