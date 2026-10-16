define dso_local void @_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m(ptr noundef nonnull readonly align 8 captures(none) dereferenceable(24) %0, ptr noundef nonnull readonly align 8 captures(none) dereferenceable(24) %1, ptr noundef nonnull readonly align 8 captures(none) dereferenceable(24) %2, i64 noundef %3) local_unnamed_addr #0 {
  %5 = icmp eq i64 %3, 0
  br i1 %5, label %29, label %6

6:                                                ; preds = %4
  %7 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = load ptr, ptr %1, align 8
  %10 = ptrtoint ptr %8 to i64
  %11 = ptrtoint ptr %9 to i64
  %12 = sub i64 %10, %11
  %13 = ashr exact i64 %12, 2
  %14 = getelementptr inbounds nuw i8, ptr %2, i64 8
  %15 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %16 = add i64 %3, -1
  br label %17

17:                                               ; preds = %6, %30
  %18 = phi i64 [ 0, %6 ], [ %33, %30 ]
  %19 = phi i64 [ 0, %6 ], [ %32, %30 ]
  %20 = phi i64 [ 0, %6 ], [ %31, %30 ]
  %21 = mul i64 %20, %3
  %22 = load ptr, ptr %14, align 8
  %23 = load ptr, ptr %2, align 8
  %24 = ptrtoint ptr %22 to i64
  %25 = ptrtoint ptr %23 to i64
  %26 = sub i64 %24, %25
  %27 = ashr exact i64 %26, 2
  br label %35

28:                                               ; preds = %30
  br label %29

29:                                               ; preds = %28, %4
  ret void

30:                                               ; preds = %64
  %31 = add nuw i64 %20, 1
  %32 = sub i64 %19, %3
  %33 = add i64 %18, %3
  %34 = icmp eq i64 %31, %3
  br i1 %34, label %28, label %17

35:                                               ; preds = %17, %64
  %36 = phi i64 [ 0, %17 ], [ %67, %64 ]
  %37 = phi i64 [ 0, %17 ], [ %66, %64 ]
  %38 = phi i64 [ 0, %17 ], [ %65, %64 ]
  %39 = add nuw i64 %38, %21
  %40 = icmp ult i64 %39, %13
  br i1 %40, label %42, label %41

41:                                               ; preds = %35
  tail call void @llvm.trap()
  unreachable

42:                                               ; preds = %35
  %43 = call i64 @llvm.umax.i64(i64 %27, i64 %37)
  %44 = add i64 %43, %36
  %45 = getelementptr inbounds nuw i32, ptr %9, i64 %39
  %46 = load i32, ptr %45, align 4
  %47 = mul i64 %38, %3
  %48 = load ptr, ptr %15, align 8
  %49 = load ptr, ptr %0, align 8
  %50 = ptrtoint ptr %48 to i64
  %51 = ptrtoint ptr %49 to i64
  %52 = sub i64 %50, %51
  %53 = ashr exact i64 %52, 2
  %54 = call i64 @llvm.umax.i64(i64 %53, i64 %18)
  %55 = add i64 %19, %54
  %56 = freeze i64 %55
  %57 = call i64 @llvm.umin.i64(i64 %56, i64 %16)
  %58 = icmp ugt i64 %44, %57
  br i1 %58, label %59, label %79

59:                                               ; preds = %42
  %60 = icmp ugt i64 %56, %16
  br i1 %60, label %61, label %80

61:                                               ; preds = %59
  %62 = getelementptr i32, ptr %23, i64 %47
  %63 = getelementptr i32, ptr %49, i64 %21
  br label %69

64:                                               ; preds = %69
  %65 = add nuw i64 %38, 1
  %66 = add i64 %37, %3
  %67 = sub i64 %36, %3
  %68 = icmp eq i64 %65, %3
  br i1 %68, label %30, label %35

69:                                               ; preds = %61, %69
  %70 = phi i64 [ 0, %61 ], [ %77, %69 ]
  %71 = getelementptr i32, ptr %62, i64 %70
  %72 = load i32, ptr %71, align 4
  %73 = mul nsw i32 %72, %46
  %74 = getelementptr i32, ptr %63, i64 %70
  %75 = load i32, ptr %74, align 4
  %76 = add nsw i32 %75, %73
  store i32 %76, ptr %74, align 4
  %77 = add nuw i64 %70, 1
  %78 = icmp eq i64 %77, %3
  br i1 %78, label %64, label %69

79:                                               ; preds = %42
  tail call void @llvm.trap()
  unreachable

80:                                               ; preds = %59
  tail call void @llvm.trap()
  unreachable
}
