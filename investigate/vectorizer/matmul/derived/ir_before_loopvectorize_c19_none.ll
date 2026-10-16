define dso_local void @_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %2, i64 noundef %3) local_unnamed_addr #0 {
  %5 = icmp eq i64 %3, 0
  br i1 %5, label %16, label %6

6:                                                ; preds = %4
  %7 = load ptr, ptr %1, align 8
  %8 = load ptr, ptr %2, align 8
  %9 = load ptr, ptr %0, align 8
  br label %10

10:                                               ; preds = %6, %17
  %11 = phi i64 [ 0, %6 ], [ %18, %17 ]
  %12 = mul i64 %11, %3
  %13 = getelementptr i32, ptr %7, i64 %12
  %14 = getelementptr i32, ptr %9, i64 %12
  br label %20

15:                                               ; preds = %17
  br label %16

16:                                               ; preds = %15, %4
  ret void

17:                                               ; preds = %26
  %18 = add nuw i64 %11, 1
  %19 = icmp eq i64 %18, %3
  br i1 %19, label %15, label %10

20:                                               ; preds = %10, %26
  %21 = phi i64 [ 0, %10 ], [ %27, %26 ]
  %22 = getelementptr i32, ptr %13, i64 %21
  %23 = load i32, ptr %22, align 4
  %24 = mul i64 %21, %3
  %25 = getelementptr i32, ptr %8, i64 %24
  br label %29

26:                                               ; preds = %29
  %27 = add nuw i64 %21, 1
  %28 = icmp eq i64 %27, %3
  br i1 %28, label %17, label %20

29:                                               ; preds = %20, %29
  %30 = phi i64 [ 0, %20 ], [ %37, %29 ]
  %31 = getelementptr i32, ptr %25, i64 %30
  %32 = load i32, ptr %31, align 4
  %33 = mul nsw i32 %32, %23
  %34 = getelementptr i32, ptr %14, i64 %30
  %35 = load i32, ptr %34, align 4
  %36 = add nsw i32 %35, %33
  store i32 %36, ptr %34, align 4
  %37 = add nuw i64 %30, 1
  %38 = icmp eq i64 %37, %3
  br i1 %38, label %26, label %29
}
