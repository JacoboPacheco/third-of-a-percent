define dso_local void @_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m(ptr nofree noundef nonnull readonly align 8 captures(none) dereferenceable(24) %0, ptr nofree noundef nonnull readonly align 8 captures(none) dereferenceable(24) %1, ptr nofree noundef nonnull readonly align 8 captures(none) dereferenceable(24) %2, i64 noundef %3) local_unnamed_addr #0 {
  %5 = icmp eq i64 %3, 0
  br i1 %5, label %20, label %6

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
  br label %16

16:                                               ; preds = %6, %21
  %17 = phi i64 [ 0, %6 ], [ %22, %21 ]
  %18 = mul i64 %17, %3
  br label %24

19:                                               ; preds = %21
  br label %20

20:                                               ; preds = %19, %4
  ret void

21:                                               ; preds = %39
  %22 = add nuw i64 %17, 1
  %23 = icmp eq i64 %22, %3
  br i1 %23, label %19, label %16

24:                                               ; preds = %16, %39
  %25 = phi i64 [ 0, %16 ], [ %40, %39 ]
  %26 = add nuw i64 %25, %18
  %27 = icmp ult i64 %26, %13
  br i1 %27, label %29, label %28

28:                                               ; preds = %24
  tail call void @llvm.trap()
  unreachable

29:                                               ; preds = %24
  %30 = getelementptr inbounds nuw [4 x i8], ptr %9, i64 %26
  %31 = load i32, ptr %30, align 4
  %32 = mul i64 %25, %3
  %33 = load ptr, ptr %14, align 8
  %34 = load ptr, ptr %2, align 8
  %35 = ptrtoint ptr %33 to i64
  %36 = ptrtoint ptr %34 to i64
  %37 = sub i64 %35, %36
  %38 = ashr exact i64 %37, 2
  br label %42

39:                                               ; preds = %57
  %40 = add nuw i64 %25, 1
  %41 = icmp eq i64 %40, %3
  br i1 %41, label %21, label %24

42:                                               ; preds = %29, %57
  %43 = phi i64 [ 0, %29 ], [ %64, %57 ]
  %44 = add nuw i64 %43, %32
  %45 = icmp ult i64 %44, %38
  br i1 %45, label %47, label %46

46:                                               ; preds = %42
  tail call void @llvm.trap()
  unreachable

47:                                               ; preds = %42
  %48 = add nuw i64 %43, %18
  %49 = load ptr, ptr %15, align 8
  %50 = load ptr, ptr %0, align 8
  %51 = ptrtoint ptr %49 to i64
  %52 = ptrtoint ptr %50 to i64
  %53 = sub i64 %51, %52
  %54 = ashr exact i64 %53, 2
  %55 = icmp ult i64 %48, %54
  br i1 %55, label %57, label %56

56:                                               ; preds = %47
  tail call void @llvm.trap()
  unreachable

57:                                               ; preds = %47
  %58 = getelementptr inbounds nuw [4 x i8], ptr %34, i64 %44
  %59 = load i32, ptr %58, align 4
  %60 = mul nsw i32 %59, %31
  %61 = getelementptr inbounds nuw [4 x i8], ptr %50, i64 %48
  %62 = load i32, ptr %61, align 4
  %63 = add nsw i32 %62, %60
  store i32 %63, ptr %61, align 4
  %64 = add nuw i64 %43, 1
  %65 = icmp eq i64 %64, %3
  br i1 %65, label %39, label %42
}
