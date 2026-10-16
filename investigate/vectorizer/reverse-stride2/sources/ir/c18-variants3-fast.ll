; Standalone module made from the IR dumps in raw/B-c18-variants3-fast-ir.json (see extract.py).
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%"class.std::__1::vector" = type { ptr, ptr, ptr }

declare void @llvm.assume(i1 noundef)
declare void @llvm.trap() #9999
declare i64 @llvm.umax.i64(i64, i64)
declare i64 @llvm.umin.i64(i64, i64)

; *** IR Dump Before LoopVectorizePass on _Z12v3_one_plainRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z12v3_one_plainRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %8 = load ptr, ptr %7, align 8
  %9 = ptrtoint ptr %8 to i64
  %10 = ptrtoint ptr %4 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = icmp eq ptr %6, %3
  br i1 %13, label %bb21, label %bb14

bb14:                                               ; preds = %entry
  %15 = ptrtoint ptr %6 to i64
  %16 = ptrtoint ptr %3 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %18, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb28
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb14, %bb28
  %23 = phi i64 [ %35, %bb28 ], [ 0, %bb14 ]
  %24 = shl i64 %23, 1
  %25 = or disjoint i64 %24, 1
  %26 = icmp ult i64 %25, %12
  br i1 %26, label %bb28, label %bb27

bb27:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb28:                                               ; preds = %bb22
  %29 = getelementptr inbounds i32, ptr %4, i64 %24
  %30 = load i32, ptr %29, align 4
  %31 = getelementptr inbounds i32, ptr %4, i64 %25
  %32 = load i32, ptr %31, align 4
  %33 = add nsw i32 %32, %30
  %34 = getelementptr inbounds i32, ptr %3, i64 %23
  store i32 %33, ptr %34, align 4
  %35 = add nuw i64 %23, 1
  %36 = icmp eq i64 %35, %19
  br i1 %36, label %bb20, label %bb22
}


; *** IR Dump Before LoopVectorizePass on _Z11v3_one_halfRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z11v3_one_halfRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = icmp eq ptr %6, %3
  br i1 %7, label %bb22, label %bb8

bb8:                                                ; preds = %entry
  %9 = ptrtoint ptr %6 to i64
  %10 = ptrtoint ptr %3 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %14 = load ptr, ptr %13, align 8
  %15 = ptrtoint ptr %14 to i64
  %16 = ptrtoint ptr %4 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = lshr i64 %18, 1
  %20 = call i64 @llvm.umax.i64(i64 %12, i64 1)
  br label %bb23

bb21:                                               ; preds = %bb27
  br label %bb22

bb22:                                               ; preds = %bb21, %entry
  ret void

bb23:                                               ; preds = %bb8, %bb27
  %24 = phi i64 [ 0, %bb8 ], [ %36, %bb27 ]
  %25 = icmp eq i64 %24, %19
  br i1 %25, label %bb26, label %bb27

bb26:                                               ; preds = %bb23
  tail call void @llvm.trap()
  unreachable

bb27:                                               ; preds = %bb23
  %28 = shl nuw i64 %24, 1
  %29 = getelementptr inbounds i32, ptr %4, i64 %28
  %30 = load i32, ptr %29, align 4
  %31 = or disjoint i64 %28, 1
  %32 = getelementptr inbounds i32, ptr %4, i64 %31
  %33 = load i32, ptr %32, align 4
  %34 = add nsw i32 %33, %30
  %35 = getelementptr inbounds i32, ptr %3, i64 %24
  store i32 %34, ptr %35, align 4
  %36 = add nuw i64 %24, 1
  %37 = icmp eq i64 %36, %20
  br i1 %37, label %bb21, label %bb23
}


; *** IR Dump Before LoopVectorizePass on _Z10v3_one_minRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z10v3_one_minRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = icmp eq ptr %6, %3
  br i1 %7, label %bb23, label %bb8

bb8:                                                ; preds = %entry
  %9 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = ptrtoint ptr %10 to i64
  %12 = ptrtoint ptr %4 to i64
  %13 = sub i64 %11, %12
  %14 = ashr exact i64 %13, 2
  %15 = tail call i64 @llvm.umin.i64(i64 %14, i64 1099511627776)
  %16 = ptrtoint ptr %6 to i64
  %17 = ptrtoint ptr %3 to i64
  %18 = sub i64 %16, %17
  %19 = ashr exact i64 %18, 2
  %20 = lshr i64 %15, 1
  %21 = call i64 @llvm.umax.i64(i64 %19, i64 1)
  br label %bb24

bb22:                                               ; preds = %bb28
  br label %bb23

bb23:                                               ; preds = %bb22, %entry
  ret void

bb24:                                               ; preds = %bb8, %bb28
  %25 = phi i64 [ %37, %bb28 ], [ 0, %bb8 ]
  %26 = icmp eq i64 %25, %20
  br i1 %26, label %bb27, label %bb28

bb27:                                               ; preds = %bb24
  tail call void @llvm.trap()
  unreachable

bb28:                                               ; preds = %bb24
  %29 = shl nuw i64 %25, 1
  %30 = or disjoint i64 %29, 1
  %31 = getelementptr inbounds i32, ptr %4, i64 %29
  %32 = load i32, ptr %31, align 4
  %33 = getelementptr inbounds i32, ptr %4, i64 %30
  %34 = load i32, ptr %33, align 4
  %35 = add nsw i32 %34, %32
  %36 = getelementptr inbounds i32, ptr %3, i64 %25
  store i32 %35, ptr %36, align 4
  %37 = add nuw nsw i64 %25, 1
  %38 = icmp eq i64 %37, %21
  br i1 %38, label %bb22, label %bb24
}


; *** IR Dump Before LoopVectorizePass on _Z13v3_one_assumeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z13v3_one_assumeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %8 = load ptr, ptr %7, align 8
  %9 = ptrtoint ptr %8 to i64
  %10 = ptrtoint ptr %4 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = icmp ult i64 %12, 1099511627776
  tail call void @llvm.assume(i1 %13)
  %14 = icmp eq ptr %6, %3
  br i1 %14, label %bb23, label %bb15

bb15:                                               ; preds = %entry
  %16 = ptrtoint ptr %6 to i64
  %17 = ptrtoint ptr %3 to i64
  %18 = sub i64 %16, %17
  %19 = ashr exact i64 %18, 2
  %20 = lshr i64 %12, 1
  %21 = call i64 @llvm.umax.i64(i64 %19, i64 1)
  br label %bb24

bb22:                                               ; preds = %bb28
  br label %bb23

bb23:                                               ; preds = %bb22, %entry
  ret void

bb24:                                               ; preds = %bb15, %bb28
  %25 = phi i64 [ %37, %bb28 ], [ 0, %bb15 ]
  %26 = icmp eq i64 %25, %20
  br i1 %26, label %bb27, label %bb28

bb27:                                               ; preds = %bb24
  tail call void @llvm.trap()
  unreachable

bb28:                                               ; preds = %bb24
  %29 = shl nuw i64 %25, 1
  %30 = or disjoint i64 %29, 1
  %31 = getelementptr inbounds i32, ptr %4, i64 %29
  %32 = load i32, ptr %31, align 4
  %33 = getelementptr inbounds i32, ptr %4, i64 %30
  %34 = load i32, ptr %33, align 4
  %35 = add nsw i32 %34, %32
  %36 = getelementptr inbounds i32, ptr %3, i64 %25
  store i32 %35, ptr %36, align 4
  %37 = add nuw nsw i64 %25, 1
  %38 = icmp eq i64 %37, %21
  br i1 %38, label %bb22, label %bb24
}


; *** IR Dump Before LoopVectorizePass on _Z12v3_two_plainRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z12v3_two_plainRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %8 = load ptr, ptr %7, align 8
  %9 = ptrtoint ptr %8 to i64
  %10 = ptrtoint ptr %4 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = icmp eq ptr %6, %3
  br i1 %13, label %bb21, label %bb14

bb14:                                               ; preds = %entry
  %15 = ptrtoint ptr %6 to i64
  %16 = ptrtoint ptr %3 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %18, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb31
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb14, %bb31
  %23 = phi i64 [ %38, %bb31 ], [ 0, %bb14 ]
  %24 = shl i64 %23, 1
  %25 = icmp ult i64 %24, %12
  br i1 %25, label %bb27, label %bb26

bb26:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb27:                                               ; preds = %bb22
  %28 = or disjoint i64 %24, 1
  %29 = icmp ult i64 %28, %12
  br i1 %29, label %bb31, label %bb30

bb30:                                               ; preds = %bb27
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb27
  %32 = getelementptr inbounds i32, ptr %4, i64 %24
  %33 = load i32, ptr %32, align 4
  %34 = getelementptr inbounds i32, ptr %4, i64 %28
  %35 = load i32, ptr %34, align 4
  %36 = add nsw i32 %35, %33
  %37 = getelementptr inbounds i32, ptr %3, i64 %23
  store i32 %36, ptr %37, align 4
  %38 = add nuw i64 %23, 1
  %39 = icmp eq i64 %38, %19
  br i1 %39, label %bb20, label %bb22
}


; *** IR Dump Before LoopVectorizePass on _Z13v3_two_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z13v3_two_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = icmp eq ptr %6, %3
  br i1 %7, label %bb25, label %bb8

bb8:                                                ; preds = %entry
  %9 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = ptrtoint ptr %10 to i64
  %12 = ptrtoint ptr %4 to i64
  %13 = sub i64 %11, %12
  %14 = ashr exact i64 %13, 2
  %15 = and i64 %14, 9223372036854775807
  %16 = ptrtoint ptr %6 to i64
  %17 = ptrtoint ptr %3 to i64
  %18 = sub i64 %16, %17
  %19 = ashr exact i64 %18, 2
  %20 = add nuw i64 %15, 1
  %21 = lshr i64 %20, 1
  %22 = lshr i64 %15, 1
  %23 = call i64 @llvm.umax.i64(i64 %19, i64 1)
  br label %bb26

bb24:                                               ; preds = %bb34
  br label %bb25

bb25:                                               ; preds = %bb24, %entry
  ret void

bb26:                                               ; preds = %bb8, %bb34
  %27 = phi i64 [ %42, %bb34 ], [ 0, %bb8 ]
  %28 = shl nuw i64 %27, 1
  %29 = icmp eq i64 %27, %21
  br i1 %29, label %bb30, label %bb31

bb30:                                               ; preds = %bb26
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb26
  %32 = icmp eq i64 %27, %22
  br i1 %32, label %bb33, label %bb34

bb33:                                               ; preds = %bb31
  tail call void @llvm.trap()
  unreachable

bb34:                                               ; preds = %bb31
  %35 = or disjoint i64 %28, 1
  %36 = getelementptr inbounds i32, ptr %4, i64 %28
  %37 = load i32, ptr %36, align 4
  %38 = getelementptr inbounds i32, ptr %4, i64 %35
  %39 = load i32, ptr %38, align 4
  %40 = add nsw i32 %39, %37
  %41 = getelementptr inbounds i32, ptr %3, i64 %27
  store i32 %40, ptr %41, align 4
  %42 = add nuw nsw i64 %27, 1
  %43 = icmp eq i64 %42, %23
  br i1 %43, label %bb24, label %bb26
}

attributes #0 = { mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable }
attributes #9999 = { cold noreturn nounwind memory(inaccessiblemem: write) }
