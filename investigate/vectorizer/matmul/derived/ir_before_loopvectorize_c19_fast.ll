define dso_local void @_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %2, i64 noundef %3) local_unnamed_addr #0 {
  %5 = icmp eq i64 %3, 0
  br i1 %5, label %26, label %6

6:                                                ; preds = %4
  %7 = getelementptr inbounds i8, ptr %1, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = load ptr, ptr %1, align 8
  %10 = ptrtoint ptr %8 to i64
  %11 = ptrtoint ptr %9 to i64
  %12 = sub i64 %10, %11
  %13 = ashr exact i64 %12, 2
  %14 = getelementptr inbounds i8, ptr %2, i64 8
  %15 = getelementptr inbounds i8, ptr %0, i64 8
  br label %16

16:                                               ; preds = %6, %27
  %17 = phi i64 [ 0, %6 ], [ %28, %27 ]
  %18 = mul i64 %17, %3
  %19 = load ptr, ptr %14, align 8
  %20 = load ptr, ptr %2, align 8
  %21 = ptrtoint ptr %19 to i64
  %22 = ptrtoint ptr %20 to i64
  %23 = sub i64 %21, %22
  %24 = ashr exact i64 %23, 2
  br label %30

25:                                               ; preds = %27
  br label %26

26:                                               ; preds = %25, %4
  ret void

27:                                               ; preds = %45
  %28 = add nuw i64 %17, 1
  %29 = icmp eq i64 %28, %3
  br i1 %29, label %25, label %16

30:                                               ; preds = %16, %45
  %31 = phi i64 [ 0, %16 ], [ %46, %45 ]
  %32 = add nuw i64 %31, %18
  %33 = icmp ugt i64 %13, %32
  br i1 %33, label %35, label %34

34:                                               ; preds = %30
  tail call void @llvm.trap()
  unreachable

35:                                               ; preds = %30
  %36 = getelementptr inbounds i32, ptr %9, i64 %32
  %37 = load i32, ptr %36, align 4
  %38 = mul i64 %31, %3
  %39 = load ptr, ptr %15, align 8
  %40 = load ptr, ptr %0, align 8
  %41 = ptrtoint ptr %39 to i64
  %42 = ptrtoint ptr %40 to i64
  %43 = sub i64 %41, %42
  %44 = ashr exact i64 %43, 2
  br label %48

45:                                               ; preds = %57
  %46 = add nuw i64 %31, 1
  %47 = icmp eq i64 %46, %3
  br i1 %47, label %27, label %30

48:                                               ; preds = %35, %57
  %49 = phi i64 [ 0, %35 ], [ %64, %57 ]
  %50 = add nuw i64 %49, %38
  %51 = icmp ugt i64 %24, %50
  br i1 %51, label %53, label %52

52:                                               ; preds = %48
  tail call void @llvm.trap()
  unreachable

53:                                               ; preds = %48
  %54 = add nuw i64 %49, %18
  %55 = icmp ugt i64 %44, %54
  br i1 %55, label %57, label %56

56:                                               ; preds = %53
  tail call void @llvm.trap()
  unreachable

57:                                               ; preds = %53
  %58 = getelementptr inbounds i32, ptr %20, i64 %50
  %59 = load i32, ptr %58, align 4
  %60 = mul nsw i32 %59, %37
  %61 = getelementptr inbounds i32, ptr %40, i64 %54
  %62 = load i32, ptr %61, align 4
  %63 = add nsw i32 %62, %60
  store i32 %63, ptr %61, align 4
  %64 = add nuw i64 %49, 1
  %65 = icmp eq i64 %64, %3
  br i1 %65, label %45, label %48
}
