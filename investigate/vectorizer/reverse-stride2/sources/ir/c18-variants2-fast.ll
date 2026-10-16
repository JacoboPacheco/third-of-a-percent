; Standalone module made from the IR dumps in raw/B-c18-variants2-fast-ir.json (see extract.py).
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%"class.std::__1::vector" = type { ptr, ptr, ptr }

declare void @llvm.trap() #9999
declare i64 @llvm.umax.i64(i64, i64)

; *** IR Dump Before LoopVectorizePass on _Z11v2_s2_guardRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z11v2_s2_guardRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = ptrtoint ptr %6 to i64
  %8 = ptrtoint ptr %3 to i64
  %9 = sub i64 %7, %8
  %10 = ashr exact i64 %9, 2
  %11 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %12 = load ptr, ptr %11, align 8
  %13 = ptrtoint ptr %12 to i64
  %14 = ptrtoint ptr %4 to i64
  %15 = sub i64 %13, %14
  %16 = ashr exact i64 %15, 2
  %17 = icmp sgt i64 %10, -1
  br i1 %17, label %bb18, label %bb22

bb18:                                               ; preds = %entry
  %19 = icmp eq ptr %6, %3
  br i1 %19, label %bb24, label %bb20

bb20:                                               ; preds = %bb18
  %21 = call i64 @llvm.umax.i64(i64 %10, i64 1)
  br label %bb25

bb22:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb23:                                               ; preds = %bb31
  br label %bb24

bb24:                                               ; preds = %bb23, %bb18
  ret void

bb25:                                               ; preds = %bb20, %bb31
  %26 = phi i64 [ %38, %bb31 ], [ 0, %bb20 ]
  %27 = shl nuw i64 %26, 1
  %28 = or disjoint i64 %27, 1
  %29 = icmp ult i64 %28, %16
  br i1 %29, label %bb31, label %bb30

bb30:                                               ; preds = %bb25
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb25
  %32 = getelementptr inbounds i32, ptr %4, i64 %27
  %33 = load i32, ptr %32, align 4
  %34 = getelementptr inbounds i32, ptr %4, i64 %28
  %35 = load i32, ptr %34, align 4
  %36 = add nsw i32 %35, %33
  %37 = getelementptr inbounds i32, ptr %3, i64 %26
  store i32 %36, ptr %37, align 4
  %38 = add nuw i64 %26, 1
  %39 = icmp eq i64 %38, %21
  br i1 %39, label %bb23, label %bb25
}


; *** IR Dump Before LoopVectorizePass on _Z18v2_s2_guard_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z18v2_s2_guard_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = ptrtoint ptr %6 to i64
  %8 = ptrtoint ptr %3 to i64
  %9 = sub i64 %7, %8
  %10 = ashr exact i64 %9, 2
  %11 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %12 = load ptr, ptr %11, align 8
  %13 = ptrtoint ptr %12 to i64
  %14 = ptrtoint ptr %4 to i64
  %15 = sub i64 %13, %14
  %16 = ashr exact i64 %15, 2
  %17 = icmp sgt i64 %10, -1
  br i1 %17, label %bb18, label %bb24

bb18:                                               ; preds = %entry
  %19 = icmp eq ptr %6, %3
  br i1 %19, label %bb26, label %bb20

bb20:                                               ; preds = %bb18
  %21 = lshr i64 %16, 1
  %22 = and i64 %21, 4611686018427387903
  %23 = call i64 @llvm.umax.i64(i64 %10, i64 1)
  br label %bb27

bb24:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb25:                                               ; preds = %bb31
  br label %bb26

bb26:                                               ; preds = %bb25, %bb18
  ret void

bb27:                                               ; preds = %bb20, %bb31
  %28 = phi i64 [ %40, %bb31 ], [ 0, %bb20 ]
  %29 = icmp eq i64 %28, %22
  br i1 %29, label %bb30, label %bb31

bb30:                                               ; preds = %bb27
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb27
  %32 = shl nuw i64 %28, 1
  %33 = or disjoint i64 %32, 1
  %34 = getelementptr inbounds i32, ptr %4, i64 %32
  %35 = load i32, ptr %34, align 4
  %36 = getelementptr inbounds i32, ptr %4, i64 %33
  %37 = load i32, ptr %36, align 4
  %38 = add nsw i32 %37, %35
  %39 = getelementptr inbounds i32, ptr %3, i64 %28
  store i32 %38, ptr %39, align 4
  %40 = add nuw nsw i64 %28, 1
  %41 = icmp eq i64 %40, %23
  br i1 %41, label %bb25, label %bb27
}


; *** IR Dump Before LoopVectorizePass on _Z12v2_s2_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z12v2_s2_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
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
  %15 = ptrtoint ptr %6 to i64
  %16 = ptrtoint ptr %3 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = lshr i64 %14, 1
  %20 = and i64 %19, 4611686018427387903
  %21 = call i64 @llvm.umax.i64(i64 %18, i64 1)
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


; *** IR Dump Before LoopVectorizePass on _Z13v2_rev_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z13v2_rev_maskedRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %6 = load ptr, ptr %5, align 8
  %7 = icmp eq ptr %6, %4
  br i1 %7, label %bb23, label %bb8

bb8:                                                ; preds = %entry
  %9 = ptrtoint ptr %6 to i64
  %10 = ptrtoint ptr %4 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %14 = load ptr, ptr %13, align 8
  %15 = ptrtoint ptr %14 to i64
  %16 = ptrtoint ptr %3 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = and i64 %18, 9223372036854775807
  %20 = add nsw i64 %12, -1
  %21 = icmp ult i64 %20, %19
  br label %bb24

bb22:                                               ; preds = %bb27
  br label %bb23

bb23:                                               ; preds = %bb22, %entry
  ret void

bb24:                                               ; preds = %bb8, %bb27
  %25 = phi i64 [ %28, %bb27 ], [ %12, %bb8 ]
  br i1 %21, label %bb27, label %bb26

bb26:                                               ; preds = %bb24
  tail call void @llvm.trap()
  unreachable

bb27:                                               ; preds = %bb24
  %28 = add nsw i64 %25, -1
  %29 = getelementptr inbounds i32, ptr %4, i64 %28
  %30 = load i32, ptr %29, align 4
  %31 = shl nsw i32 %30, 1
  %32 = getelementptr inbounds i32, ptr %3, i64 %28
  store i32 %31, ptr %32, align 4
  %33 = icmp eq i64 %28, 0
  br i1 %33, label %bb22, label %bb24
}

attributes #0 = { mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable }
attributes #9999 = { cold noreturn nounwind memory(inaccessiblemem: write) }
