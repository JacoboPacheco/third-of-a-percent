; Standalone module made from the IR dumps in raw/B-c19-kernels-fast-ir.json (see extract.py).
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%"class.std::__1::vector" = type { ptr, ptr, ptr }

declare void @llvm.trap() #9999
declare i64 @llvm.umax.i64(i64, i64)

; *** IR Dump Before LoopVectorizePass on _Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE ***
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(read, inaccessiblemem: none) uwtable
define dso_local noundef i64 @_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0) local_unnamed_addr #0 {
entry:
  %2 = getelementptr inbounds i8, ptr %0, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = load ptr, ptr %0, align 8
  %5 = icmp eq ptr %3, %4
  br i1 %5, label %bb14, label %bb6

bb6:                                                ; preds = %entry
  %7 = ptrtoint ptr %3 to i64
  %8 = ptrtoint ptr %4 to i64
  %9 = sub i64 %7, %8
  %10 = ashr exact i64 %9, 2
  %11 = call i64 @llvm.umax.i64(i64 %10, i64 1)
  br label %bb16

bb12:                                               ; preds = %bb16
  %13 = phi i64 [ %22, %bb16 ]
  br label %bb14

bb14:                                               ; preds = %bb12, %entry
  %15 = phi i64 [ 0, %entry ], [ %13, %bb12 ]
  ret i64 %15

bb16:                                               ; preds = %bb6, %bb16
  %17 = phi i64 [ %23, %bb16 ], [ 0, %bb6 ]
  %18 = phi i64 [ %22, %bb16 ], [ 0, %bb6 ]
  %19 = getelementptr inbounds i32, ptr %4, i64 %17
  %20 = load i32, ptr %19, align 4
  %21 = sext i32 %20 to i64
  %22 = add nsw i64 %18, %21
  %23 = add nuw i64 %17, 1
  %24 = icmp eq i64 %23, %11
  br i1 %24, label %bb12, label %bb16
}


; *** IR Dump Before LoopVectorizePass on _Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %2) local_unnamed_addr #1 {
entry:
  %4 = getelementptr inbounds i8, ptr %1, i64 8
  %5 = load ptr, ptr %4, align 8
  %6 = load ptr, ptr %1, align 8
  %7 = icmp eq ptr %5, %6
  br i1 %7, label %bb29, label %bb8

bb8:                                                ; preds = %entry
  %9 = ptrtoint ptr %5 to i64
  %10 = ptrtoint ptr %6 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = getelementptr inbounds i8, ptr %2, i64 8
  %14 = load ptr, ptr %13, align 8
  %15 = load ptr, ptr %2, align 8
  %16 = ptrtoint ptr %14 to i64
  %17 = ptrtoint ptr %15 to i64
  %18 = sub i64 %16, %17
  %19 = ashr exact i64 %18, 2
  %20 = getelementptr inbounds i8, ptr %0, i64 8
  %21 = load ptr, ptr %20, align 8
  %22 = load ptr, ptr %0, align 8
  %23 = ptrtoint ptr %21 to i64
  %24 = ptrtoint ptr %22 to i64
  %25 = sub i64 %23, %24
  %26 = ashr exact i64 %25, 2
  %27 = call i64 @llvm.umax.i64(i64 %12, i64 1)
  br label %bb30

bb28:                                               ; preds = %bb37
  br label %bb29

bb29:                                               ; preds = %bb28, %entry
  ret void

bb30:                                               ; preds = %bb8, %bb37
  %31 = phi i64 [ 0, %bb8 ], [ %44, %bb37 ]
  %32 = icmp eq i64 %31, %19
  br i1 %32, label %bb33, label %bb34

bb33:                                               ; preds = %bb30
  tail call void @llvm.trap()
  unreachable

bb34:                                               ; preds = %bb30
  %35 = icmp eq i64 %31, %26
  br i1 %35, label %bb36, label %bb37

bb36:                                               ; preds = %bb34
  tail call void @llvm.trap()
  unreachable

bb37:                                               ; preds = %bb34
  %38 = getelementptr inbounds i32, ptr %6, i64 %31
  %39 = load i32, ptr %38, align 4
  %40 = getelementptr inbounds i32, ptr %15, i64 %31
  %41 = load i32, ptr %40, align 4
  %42 = add nsw i32 %41, %39
  %43 = getelementptr inbounds i32, ptr %22, i64 %31
  store i32 %42, ptr %43, align 4
  %44 = add nuw i64 %31, 1
  %45 = icmp eq i64 %44, %27
  br i1 %45, label %bb28, label %bb30
}


; *** IR Dump Before LoopVectorizePass on _Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #1 {
entry:
  %3 = getelementptr inbounds i8, ptr %1, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = icmp ugt i64 %9, 2
  br i1 %10, label %bb11, label %bb23

bb11:                                               ; preds = %entry
  %12 = getelementptr inbounds i8, ptr %0, i64 8
  %13 = load ptr, ptr %12, align 8
  %14 = load ptr, ptr %0, align 8
  %15 = ptrtoint ptr %13 to i64
  %16 = ptrtoint ptr %14 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %18, i64 1)
  %20 = add i64 %19, 1
  %21 = getelementptr i8, ptr %5, i64 -4
  br label %bb24

bb22:                                               ; preds = %bb29
  br label %bb23

bb23:                                               ; preds = %bb22, %entry
  ret void

bb24:                                               ; preds = %bb11, %bb29
  %25 = phi i64 [ 2, %bb11 ], [ %39, %bb29 ]
  %26 = phi i64 [ 1, %bb11 ], [ %25, %bb29 ]
  %27 = icmp eq i64 %25, %20
  br i1 %27, label %bb28, label %bb29

bb28:                                               ; preds = %bb24
  tail call void @llvm.trap()
  unreachable

bb29:                                               ; preds = %bb24
  %30 = getelementptr i32, ptr %21, i64 %26
  %31 = load i32, ptr %30, align 4
  %32 = getelementptr inbounds i32, ptr %5, i64 %26
  %33 = load i32, ptr %32, align 4
  %34 = add nsw i32 %33, %31
  %35 = getelementptr inbounds i32, ptr %5, i64 %25
  %36 = load i32, ptr %35, align 4
  %37 = add nsw i32 %34, %36
  %38 = getelementptr inbounds i32, ptr %14, i64 %26
  store i32 %37, ptr %38, align 4
  %39 = add nuw i64 %25, 1
  %40 = icmp eq i64 %39, %9
  br i1 %40, label %bb22, label %bb24
}


; *** IR Dump Before LoopVectorizePass on _Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #1 {
entry:
  %3 = getelementptr inbounds i8, ptr %1, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = icmp eq ptr %4, %5
  br i1 %6, label %bb22, label %bb7

bb7:                                                ; preds = %entry
  %8 = ptrtoint ptr %5 to i64
  %9 = ptrtoint ptr %4 to i64
  %10 = sub i64 %9, %8
  %11 = ashr exact i64 %10, 2
  %12 = getelementptr inbounds i8, ptr %0, i64 8
  %13 = load ptr, ptr %12, align 8
  %14 = load ptr, ptr %0, align 8
  %15 = ptrtoint ptr %13 to i64
  %16 = ptrtoint ptr %14 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = add nsw i64 %11, -1
  %20 = icmp ult i64 %19, %18
  br label %bb23

bb21:                                               ; preds = %bb26
  br label %bb22

bb22:                                               ; preds = %bb21, %entry
  ret void

bb23:                                               ; preds = %bb7, %bb26
  %24 = phi i64 [ %11, %bb7 ], [ %27, %bb26 ]
  br i1 %20, label %bb26, label %bb25

bb25:                                               ; preds = %bb23
  tail call void @llvm.trap()
  unreachable

bb26:                                               ; preds = %bb23
  %27 = add i64 %24, -1
  %28 = getelementptr inbounds i32, ptr %5, i64 %27
  %29 = load i32, ptr %28, align 4
  %30 = shl nsw i32 %29, 1
  %31 = getelementptr inbounds i32, ptr %14, i64 %27
  store i32 %30, ptr %31, align 4
  %32 = icmp eq i64 %27, 0
  br i1 %32, label %bb21, label %bb23
}


; *** IR Dump Before LoopVectorizePass on _Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #1 {
entry:
  %3 = getelementptr inbounds i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %0, align 8
  %6 = icmp eq ptr %4, %5
  br i1 %6, label %bb21, label %bb7

bb7:                                                ; preds = %entry
  %8 = ptrtoint ptr %4 to i64
  %9 = ptrtoint ptr %5 to i64
  %10 = sub i64 %8, %9
  %11 = ashr exact i64 %10, 2
  %12 = getelementptr inbounds i8, ptr %1, i64 8
  %13 = load ptr, ptr %12, align 8
  %14 = load ptr, ptr %1, align 8
  %15 = ptrtoint ptr %13 to i64
  %16 = ptrtoint ptr %14 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %11, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb31
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb7, %bb31
  %23 = phi i64 [ 0, %bb7 ], [ %38, %bb31 ]
  %24 = shl i64 %23, 1
  %25 = icmp ugt i64 %18, %24
  br i1 %25, label %bb27, label %bb26

bb26:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb27:                                               ; preds = %bb22
  %28 = or disjoint i64 %24, 1
  %29 = icmp ugt i64 %18, %28
  br i1 %29, label %bb31, label %bb30

bb30:                                               ; preds = %bb27
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb27
  %32 = getelementptr inbounds i32, ptr %14, i64 %24
  %33 = load i32, ptr %32, align 4
  %34 = getelementptr inbounds i32, ptr %14, i64 %28
  %35 = load i32, ptr %34, align 4
  %36 = add nsw i32 %35, %33
  %37 = getelementptr inbounds i32, ptr %5, i64 %23
  store i32 %36, ptr %37, align 4
  %38 = add nuw i64 %23, 1
  %39 = icmp eq i64 %38, %19
  br i1 %39, label %bb20, label %bb22
}

attributes #0 = { mustprogress nofree noinline norecurse nosync nounwind willreturn memory(read, inaccessiblemem: none) uwtable }
attributes #1 = { mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable }
attributes #9999 = { cold noreturn nounwind memory(inaccessiblemem: write) }
